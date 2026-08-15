from pub_sub.entities import Message
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self, broker, name=None):
        self.id = str(uuid4())
        self.name = name or f"Publisher-{self.id[:8]}"
        self.broker = broker
        self.published_count = 0

    def publish(self, topic_name, message: Message):
        logger.info(f"{self.name} publishing message {message.message_id} to topic '{topic_name}'")
        self.broker.publish(topic_name, message)
        self.published_count += 1

    def publish_batch(self, topic_name, messages: list[Message]):
        logger.info(f"{self.name} publishing {len(messages)} messages to topic '{topic_name}'")
        for message in messages:
            self.broker.publish(topic_name, message)
            self.published_count += 1
