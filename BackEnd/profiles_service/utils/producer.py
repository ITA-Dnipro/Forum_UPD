import json
from core.settings import settings
from kafka import KafkaProducer


def send_approval_email(profile_name, updated_at, moderation_time, image_path, profile_view_url):
    topic = "profile_image"

    data = {
    "email": settings.IMAGE_MODERATOR_EMAIL,
    "profile_name": profile_name,
    "updated_at": updated_at,
    "moderation_time": moderation_time,
    "image_path": image_path, 
    "profile_view_url": profile_view_url
}


    data_bytes = json.dumps(data).encode('utf-8')
    producer = KafkaProducer(bootstrap_servers=settings.KAFKA_BROKER)
    producer.send(topic=topic, value=data_bytes, key=None, headers=None, partition=None, timestamp_ms=None)


def send_valid_profile_message(user_id, profile_type, status):
    topic = "user_role_update"
    print("message")

    data = {
    "user_id": user_id,
	"profile_type": profile_type,
	"status": status
    }
    data_bytes = json.dumps(data).encode('utf-8')
    producer = KafkaProducer(bootstrap_servers=settings.KAFKA_BROKER)
    producer.send(topic=topic, value=data_bytes, key=None, headers=None, partition=None, timestamp_ms=None)

