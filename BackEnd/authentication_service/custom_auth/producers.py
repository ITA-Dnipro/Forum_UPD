from confluent_kafka import Producer
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

KAFKA_BROKER = getattr(settings, "KAFKA_BROKER", "kafka:9092")
AUTH_TOPIC = "auth"
NEW_USER_PROFILE_TOPIC = "new_user_profile"

# Kafka producer configuration
conf = {
    'bootstrap.servers': settings.KAFKA_BROKER,
}

if getattr(settings, 'KAFKA_PRODUCER_ENABLED', True):
    auth_producer = Producer(conf)
    profile_producer = Producer(conf)

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
        # Produce message to Kafka
        auth_producer.produce(AUTH_TOPIC, value=json.dumps(message))
        auth_producer.flush()
        logger.info(f"Message sent to {AUTH_TOPIC}")
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
        # Produce message to Kafka
        profile_producer.produce(NEW_USER_PROFILE_TOPIC, value=json.dumps(message))
        profile_producer.flush()
        logger.info(f"Message sent to {NEW_USER_PROFILE_TOPIC}")
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


