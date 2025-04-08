import time
import json
import logging
import signal
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

MAX_RETRIES = 5
running = True


def handle_shutdown(signum, frame):
    global running
    logger.info(f"Received shutdown signal ({signum}). Exiting gracefully...")
    running = False


def process_role_update_message():
    global running
    retries = 0

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    while running:
        try:
            consumer = Consumer(conf)
            consumer.subscribe([USER_ROLE_UPDATE_TOPIC])
            logger.info("Kafka consumer started and subscribed to topic.")

            while running:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())

                try:
                    data = json.loads(msg.value().decode("utf-8"))

                    required_fields = ["user_id", "profile_type", "status"]
                    missing_fields = [field for field in required_fields if field not in data or data[field] is None]

                    if missing_fields:
                        logger.error(f"Invalid message: missing fields {missing_fields} — raw message: {data}")
                        continue

                    user_id = data.get("user_id")
                    profile_type = data.get("profile_type")
                    new_status = data.get("status")

                    user = CustomUser.objects.get(id=user_id)
                    role = Role.objects.get(name=profile_type.capitalize())
                    user_role = UserRole.objects.get(user=user, role=role)

                    user_role.status = new_status
                    user_role.save()

                    logger.info(f"Updated status for {user.email}: {profile_type} {new_status}")
                    consumer.commit(msg)

                except CustomUser.DoesNotExist:
                    logger.error(f"User with ID {user_id} not found")
                except Role.DoesNotExist:
                    logger.error(f"Role '{profile_type}' does not exist")
                except UserRole.DoesNotExist:
                    logger.error(f"UserRole entry not found for user {user_id} and role {profile_type}")
                except Exception as e:
                    logger.error(f"Unexpected error while processing message: {e}")

        except KafkaException as e:
            logger.error(f"Kafka error occurred: {e}")
            retries += 1
            if retries > MAX_RETRIES:
                logger.critical("Max retries reached. Shutting down consumer.")
                break
            backoff = min(2 ** retries, 30)
            logger.info(f"Retrying in {backoff} seconds...")
            time.sleep(backoff)

        except Exception as e:
            logger.error(f"Unexpected error in main consumer loop: {e}")
            break

        finally:
            try:
                consumer.close()
                logger.info("Kafka consumer closed.")
            except Exception:
                logger.warning("Failed to close Kafka consumer cleanly.")

    logger.info("Kafka consumer service stopped.")
