import json
import logging
from kafka import KafkaProducer
from django.conf import settings

logger = logging.getLogger(__name__)

KAFKA_BROKER = getattr(settings, "KAFKA_BROKER", "kafka:9092")
AUTH_TOPIC = "auth"

if getattr(settings, 'KAFKA_PRODUCER_ENABLED', True):
    producer = KafkaProducer(
        bootstrap_servers=settings.KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None,
    )

def send_message(message_type: str, email: str, link: str, name: str = None):
    """
    Sends an activation or password reset message to the Kafka topic.

    Args:
        email (str): User's email address.
        link (str): Activation or reset link for email confirmation.
        name (str): User's name.
        message_type (str): Type of message, either "activation" or "password-reset".
    """
    message = {
        "message_type": message_type,
        "email": email,
        "link": link,
        "name": name
    }

    try:
        future = producer.send(AUTH_TOPIC, value=message)
        record_metadata = future.get(timeout=10)
        logger.info(f"Message sent to {record_metadata.topic} partition {record_metadata.partition} at offset {record_metadata.offset}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

def close_producer():
    """Closes the Kafka producer gracefully."""
    try:
        producer.flush()
        producer.close()
        logger.info("Kafka producer closed successfully.")
    except Exception as e:
        logger.error(f"Error while closing Kafka producer: {e}")
