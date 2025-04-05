import json
import logging
from kafka import KafkaConsumer
from django.conf import settings
from .models import CustomUser, Role, UserRole

logger = logging.getLogger(__name__)

KAFKA_BROKER = getattr(settings, "KAFKA_BROKER", "kafka:9092")
USER_ROLE_UPDATE_TOPIC = "user_role_update"

consumer = KafkaConsumer(
    USER_ROLE_UPDATE_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    group_id="user-role-update-group",
)

def process_role_update_message(message):
    """
    Process incoming role update message and update user's role status in the database.

    Args:
        message (dict): The message containing user_id, profile_type, and status.
    """
    try:
        user_id = message.get("user_id")
        profile_type = message.get("profile_type")
        new_status = message.get("status")

        if not user_id or not profile_type or new_status not in ["validated", "not_validated"]:
            logger.error(f"Invalid message: {message}")
            return

        user = CustomUser.objects.get(id=user_id)

        role = Role.objects.get(name=profile_type.capitalize())  # Capitalize to match 'Startup' or 'Investor'

        user_role = UserRole.objects.get(user=user, role=role)

        user_role.status = new_status
        user_role.save()

        logger.info(f"Updated role status for user {user.email} to {new_status} for role {profile_type}")

    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
    except Role.DoesNotExist:
        logger.error(f"Role {profile_type} does not exist")
    except UserRole.DoesNotExist:
        logger.error(f"UserRole entry not found for user {user_id} and role {profile_type}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def consume_role_updates():
    """
    Consumes role update messages from the Kafka topic and processes them.
    """
    for message in consumer:
        process_role_update_message(message.value)

