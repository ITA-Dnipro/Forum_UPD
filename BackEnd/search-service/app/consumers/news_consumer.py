import os
import time
import json
import asyncio
import threading

from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from dotenv import load_dotenv

from app.indexes.news_service.news_article import NewsArticleDocument
from app.config import logger
from app.consumers.utils.process_published_at_field import process_timestamp_field

load_dotenv()

es_client = None


def initialize_es_client():
    global es_client
    from app.main import app
    es_client = app.state.es_client


KAFKA_NEWS_TOPIC = os.getenv("KAFKA_NEWS_TOPIC", "news-connector.news.NewsModel")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8081")


async def process_news_record(record):
    global es_client
    if es_client is None:
        initialize_es_client()

    try:
        op = record.get("op")

        if op == "d":
            doc_id = record.get("filter")
            if isinstance(doc_id, str):
                doc_id = json.loads(doc_id)

            doc_id_val = doc_id.get("_id")
            if isinstance(doc_id_val, dict):
                doc_id_val = doc_id_val["$oid"]

            if not doc_id_val:
                raise ValueError("Deletion event missing filter._id for news")

            await es_client.delete(index=NewsArticleDocument.Index.name, id=doc_id_val, ignore=[404])
            logger.info(f"Deleted news article {doc_id_val} from index '{NewsArticleDocument.Index.name}'.")
        else:
            after_data = record.get("after")

            if isinstance(after_data, str):
                after_data = json.loads(after_data)

            if not after_data:
                raise ValueError("Upsert event missing 'after' for news")

            doc_id = after_data.get("_id")
            if isinstance(doc_id, dict):
                doc_id = doc_id["$oid"]
                after_data["_id"] = doc_id

            if not doc_id:
                raise ValueError("Document missing _id for news upsert event")

            published_at = after_data.get("published_at")
            published_at = process_timestamp_field(published_at, key="$date")

            if after_data.get("deleted"):
                await es_client.delete(index=NewsArticleDocument.Index.name, id=doc_id, ignore=[404])
                logger.info(
                    f"News article {doc_id} will be excluded from index '{NewsArticleDocument.Index.name}'."
                )

            else:
                new_doc = NewsArticleDocument(
                    meta={"id": doc_id},
                    article_id=doc_id,
                    title=after_data.get("title"),
                    content=after_data.get("content"),
                    published_at=published_at
                )
                await new_doc.save(using=es_client)
                logger.info(f"Upserted news article {doc_id} into index '{NewsArticleDocument.Index.name}'.")
    except Exception as e:
        logger.exception(f"Error processing News record: {e}")


def start_news_consumer(loop: asyncio.AbstractEventLoop):
    consumer_config = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": "elasticsearch_news_group",
        "auto.offset.reset": "earliest",
        "schema.registry.url": SCHEMA_REGISTRY_URL,
    }
    consumer = AvroConsumer(consumer_config)
    consumer.subscribe([KAFKA_NEWS_TOPIC])
    logger.info(f"Subscribed to topic: {KAFKA_NEWS_TOPIC}")

    while True:
        try:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                logger.exception(f"Consumer error: {message.error()}")
                continue

            record = message.value()
            if record is None:
                continue

            logger.info("Processing News message")
            asyncio.run_coroutine_threadsafe(process_news_record(record), loop)
            time.sleep(0.1)
        except SerializerError as e:
            logger.exception(f"Deserialization error: {e}")
            continue


def run_news_consumer(loop: asyncio.AbstractEventLoop):
    news_consumer_thread = threading.Thread(
        target=start_news_consumer, args=(loop,), daemon=True
    )
    news_consumer_thread.start()
    return news_consumer_thread
