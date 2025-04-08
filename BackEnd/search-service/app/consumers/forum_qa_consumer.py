import os
import time
import threading
import asyncio

from confluent_kafka.avro import AvroConsumer
from dotenv import load_dotenv

from app.indexes.forum_service.questions import QuestionDocument
from app.config import logger

load_dotenv()

es_client = None


def initialize_es_client():
    global es_client
    from app.main import app
    es_client = app.state.es_client


def get_field_value(record: dict, key: str):
    """
    Safely extract the value from a nested field in the record.
    Returns None if the key or inner value is missing.
    """
    try:
        field = record.get(key)
        if field and isinstance(field, dict):
            return field.get("value")
    except Exception as e:
        logger.exception(f"Error extracting field '{key}': {e}")
    return None


async def process_forum_qa_record(record: dict):
    global es_client
    if es_client is None:
        initialize_es_client()

    try:
        op = record.get("op")
        if op == "d":
            source_data = record.get("before")
            if not source_data:
                logger.exception("Missing 'before' data in deletion event.")
                return
            doc_id = source_data.get("question_id")
            if doc_id is None:
                logger.exception("Missing 'question_id' in deletion event data.")
                return
            await es_client.delete(index=QuestionDocument.Index.name, id=doc_id, ignore=[404])
            logger.info(f"Deleted article {doc_id} from index '{QuestionDocument.Index.name}'.")
        else:
            after = record.get("after")
            if not after:
                logger.exception("Missing 'after' data in non-deletion event.")
                return
            doc_id = after.get("question_id")
            if doc_id is None:
                logger.exception("Missing 'question_id' in record 'after' data.")
                return

            if op == "c":
                new_doc = QuestionDocument(
                    meta={"id": doc_id},
                    author_id=get_field_value(after, "author_id"),
                    title=get_field_value(after, "title"),
                    content=get_field_value(after, "description"),
                    status=get_field_value(after, "status"),
                    likes_count=get_field_value(after, "likes_count"),
                    saves_count=get_field_value(after, "saves_count"),
                    created_at=get_field_value(after, "created_at"),
                    updated_at=get_field_value(after, "updated_at"),
                )
                await new_doc.save(using=es_client)
                logger.info(f"Upserted forum qa article {doc_id} into index '{QuestionDocument.Index.name}'.")
            elif op == "u":
                existing_doc = await QuestionDocument.get(id=doc_id, using=es_client)
                if not existing_doc:
                    logger.warning(f"Document with id {doc_id} not found for update.")
                    return

                update_fields = {}
                field_mappings = [
                    ("title", "title"),
                    ("description", "content"),
                    ("status", "status"),
                    ("likes_count", "likes_count"),
                    ("saves_count", "saves_count"),
                    ("updated_at", "updated_at"),
                ]
                for source_field, target_field in field_mappings:
                    value = get_field_value(after, source_field)
                    if value is not None:
                        update_fields[target_field] = value

                if update_fields:
                    await existing_doc.update(**update_fields)
                    await existing_doc.save(using=es_client)
                    logger.info(f"Updated forum qa article {doc_id} in index '{QuestionDocument.Index.name}'.")
                else:
                    logger.warning(f"No valid update fields provided for document {doc_id}.")
    except Exception as e:
        logger.exception(f"Error processing forum qa record: {e}")


def start_forum_qa_consumer(loop: asyncio.AbstractEventLoop):
    consumer_config = {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        "group.id": "elasticsearch_forum_qa_group",
        "auto.offset.reset": "earliest",
        "schema.registry.url": os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8081"),
    }
    topic = os.getenv("KAFKA_FORUM_QA_TOPIC", "ForumQACluster.qa_forum.questions")

    consumer = AvroConsumer(consumer_config)
    consumer.subscribe([topic])
    logger.info(f"Subscribed to topic: {topic}")

    while True:
        try:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                logger.exception(f"Consumer error: {message.error()}")
                continue

            record = message.value()
            if not record:
                continue

            logger.info("Processing Forum QA message")
            asyncio.run_coroutine_threadsafe(process_forum_qa_record(record), loop)
            time.sleep(0.1)
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            continue


def run_forum_qa_consumer(loop: asyncio.AbstractEventLoop):
    consumer_thread = threading.Thread(
        target=start_forum_qa_consumer, args=(loop,), daemon=True
    )
    consumer_thread.start()
    return consumer_thread
