import os
import time
import threading
import asyncio

from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from dotenv import load_dotenv

from app.indexes.event_service.events import EventDocument
from app.config import logger

load_dotenv()

es_client = None


def initialize_es_client():
    global es_client
    from app.main import app
    es_client = app.state.es_client


KAFKA_EVENT_TOPIC = os.getenv("KAFKA_EVENT_TOPIC", "event-connector.public.events")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8081")


async def process_event_record(record):
    global es_client
    if es_client is None:
        initialize_es_client()

    try:
        op = record.get("op")
        before = record.get("before")
        after = record.get("after")

        if op == "d":
            doc_id = before["id"]
            await es_client.delete(index=EventDocument.Index.name, id=doc_id, ignore=[404])
            logger.info(f"Deleted event article {doc_id} from index '{EventDocument.Index.name}'.")
        else:
            doc_id = after["id"]
            if after["status"] == "deleted":
                try:
                    await es_client.delete(index=EventDocument.Index.name, id=doc_id, ignore=[404])
                    logger.info(
                        f"Event article {doc_id} will be excluded from index '{EventDocument.Index.name}'."
                    )
                except Exception as e:
                    logger.exception("Article was not found in the index.")

            else:
                new_doc = EventDocument(
                    meta={"id": doc_id},
                    event_id=doc_id,
                    organizer_id=after["organizer_id"],
                    title=after["title"],
                    content=after["description"],
                    categories=None,
                    type=after["type"],
                    status=after["status"],
                    location=after["location"],
                    image=after["image"],
                    available_slots=after["available_slots"],
                    capacity=after["capacity"],
                    date=after["date"],
                    starting_time=after["starting_time"],
                )
                await new_doc.save(using=es_client)
                logger.info(f"Upserted event article {doc_id} into index '{EventDocument.Index.name}'.")
    except Exception as e:
        logger.exception(f"Error processing event record: {e}")


def start_event_consumer(loop: asyncio.AbstractEventLoop):
    consumer_config = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": "elasticsearch_event_group",
        "auto.offset.reset": "earliest",
        "schema.registry.url": SCHEMA_REGISTRY_URL,
    }
    consumer = AvroConsumer(consumer_config)
    consumer.subscribe([KAFKA_EVENT_TOPIC])
    logger.info(f"Subscribed to topic: {KAFKA_EVENT_TOPIC}")

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

            logger.info("Processing Event message")
            asyncio.run_coroutine_threadsafe(process_event_record(record), loop)
            time.sleep(0.1)
        except SerializerError as e:
            logger.exception(f"Deserialization error: {e}")
            continue


def run_event_consumer(loop: asyncio.AbstractEventLoop):
    event_consumer_thread = threading.Thread(
        target=start_event_consumer, args=(loop,), daemon=True
    )
    event_consumer_thread.start()
    return event_consumer_thread
