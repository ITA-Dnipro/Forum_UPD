import json
import logging
from confluent_kafka import Consumer, KafkaException
from django.conf import settings
from .models import CustomUser, Role, UserRole

logger = logging.getLogger(__name__)

KAFKA_BROKER = getattr(settings, "KAFKA_BROKER", "kafka:9092")
USER_ROLE_UPDATE_TOPIC = "user_role_update"

conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'user-role-update-group',
}
consumer =Consumer(conf)
consumer.subscribe([USER_ROLE_UPDATE_TOPIC])

def process_role_update_message():
    """
    Process incoming role update message and update user's role status in the database.

    Args:
        message (dict): The message containing user_id, profile_type, and status.
    """
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            try:
                data = json.loads(msg.value().decode("utf-8"))
                user_id = data.get("user_id")
                profile_type = data.get("profile_type")
                new_status = data.get("status")

                user = CustomUser.objects.get(id=user_id)
                role = Role.objects.get(name=profile_type.capitalize())  # e.g., 'Startup' or 'Investor'
                user_role = UserRole.objects.get(user=user, role=role)

                user_role.status = new_status
                user_role.save()

                logger.info(f"Updated status for {user.email}: {profile_type} → {new_status}")

            except CustomUser.DoesNotExist:
                logger.error(f"User with ID {user_id} not found")
            except Role.DoesNotExist:
                logger.error(f"Role '{profile_type}' does not exist")
            except UserRole.DoesNotExist:
                logger.error(f"UserRole entry not found for user {user_id} and role {profile_type}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

    except KeyboardInterrupt:
        logger.info("Stopping consumer...")

    finally:
        consumer.close()
        logger.info("Consumer stopped")
