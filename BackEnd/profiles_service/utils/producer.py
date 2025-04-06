import json
from core.settings import settings
from aiokafka.producer import AIOKafkaProducer
from utils.time import moderation_time_to_str, update_time_to_str

def producer_serializer(message):
    return json.dumps(message).encode('utf-8')


_producer: AIOKafkaProducer = None

async def init_producer(bootstrap_servers: str):
    global _producer
    _producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=producer_serializer)
    await _producer.start()

async def get_producer() -> AIOKafkaProducer:
    if _producer is None:
        raise RuntimeError("Kafka producer not initialized")
    return _producer

async def shutdown_producer():
    global _producer
    if _producer:
        await _producer.stop()


async def send_valid_profile_message(producer: AIOKafkaProducer, user_id, profile_type, status):
    topic = "user_role_update"
    data = {
    "user_id": user_id,
	"profile_type": profile_type,
	"status": status
    }

    await producer.send(topic=topic, value=data)


async def send_approval_email(producer: AIOKafkaProducer, profile_name, updated_at, moderation_time, image_path, profile_view_url):
    topic = "profile_image"

    data = {
    "email": settings.IMAGE_MODERATOR_EMAIL,
    "profile_name": profile_name,
    "updated_at": update_time_to_str(updated_at),
    "moderation_time": moderation_time_to_str(moderation_time),
    "image_path": image_path, 
    "profile_view_url": profile_view_url
}

    await producer.send(topic=topic, value=data, key=None, headers=None, partition=None, timestamp_ms=None)
