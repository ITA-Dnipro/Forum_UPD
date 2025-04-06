import json
import logging
from kafka import KafkaProducer
from django.conf import settings

logger = logging.getLogger(__name__)

KAFKA_BROKER = getattr(settings, "KAFKA_BROKER", "kafka:9092")
AUTH_TOPIC = "auth"
NEW_USER_PROFILE_TOPIC = "new_user_profile"

if getattr(settings, 'KAFKA_PRODUCER_ENABLED', True):
    auth_producer = KafkaProducer(
        bootstrap_servers=settings.KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None,
    )
    profile_producer = KafkaProducer(
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
        future = auth_producer.send(AUTH_TOPIC, value=message)
        record_metadata = future.get(timeout=10)
        logger.info(f"Message sent to {record_metadata.topic} partition {record_metadata.partition} at offset {record_metadata.offset}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


def send_company_profile(user_id: int, company_info: dict):
    """
    Sends a user profile message to the Kafka topic after successful registration.

    Args:
        user_id (int): The ID of the newly registered user.
        company_info (dict): Information about the company to be sent.
    """
    message = {
        "company": {
            "user_id": user_id,
            "is_startup": company_info.get("is_startup"),
            "is_legal_entity": not company_info.get("is_fop"),
            "name": company_info.get("name"),
        }
    }

    try:
        future = profile_producer.send(NEW_USER_PROFILE_TOPIC, value=message)
        record_metadata = future.get(timeout=10)
        logger.info(f"Message sent to {record_metadata.topic} partition {record_metadata.partition} at offset {record_metadata.offset}")
    except Exception as e:
        logger.error(f"Failed to send message to {NEW_USER_PROFILE_TOPIC}: {e}")

def handle_user_registration(user_id: int, company_data: list):
    """
    Handles user registration and triggers profile producer for each company.

    Args:
        user_id (int): The ID of the registered user.
        company_data (list): A list of companies (1 or 2 companies) registered by the user.
    """
    for company in company_data:
        send_company_profile(user_id, company)

def close_producer():
    """Closes the Kafka producer gracefully."""
    try:
        auth_producer.flush()
        auth_producer.close()
        profile_producer.flush()
        profile_producer.close()
        logger.info("Kafka producers closed successfully.")
    except Exception as e:
        logger.error(f"Error while closing Kafka producers: {e}")
