import json
from aiokafka import AIOKafkaConsumer
from core.settings import settings
from typing import Union
"new_user_profile",



class BaseConsumer(AIOKafkaConsumer):
    def __init__(self, topic: Union[list[str], str]):
        super().__init__(
            topic,
            bootstrap_servers=settings.KAFKA_BROKER,
            value_deserializer=self.deserializer,
            group_id="your-consumer-group",
            auto_offset_reset="earliest" 
            )

    @staticmethod
    def deserializer(message):
        try:
            return json.loads(message.decode('utf-8'))
        except json.JSONDecodeError:
            if isinstance(message, bytes):
                return message.decode('utf-8')
            else:
                return message


class ConsumerManager:

    _instance = None
    consumers = []

    def __new__(self):
        if self._instance is None:
            return super.__new__()
        return self._instance


    @classmethod
    async def create_consumer(cls, topic):
        consumer = BaseConsumer(topic=topic)
        await consumer.start()
        cls.consumers.append(consumer)
        return consumer
    
    @classmethod
    async def shutdown_all(cls):
        for consumer in cls.consumers:
            await consumer.stop()
