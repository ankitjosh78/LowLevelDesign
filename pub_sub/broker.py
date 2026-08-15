from pub_sub.entities import Message
from pub_sub.topic import Topic
from pub_sub.subscriber import Subscriber
import threading
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class MessageBroker:
    def __init__(self, max_workers=6):
        self.topics: dict[str, Topic] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()

    def create_topic(self, topic_name):
        if topic_name not in self.topics:
            with self._lock:
                if topic_name not in self.topics:
                    self.topics[topic_name] = Topic(topic_name, self.executor)
                    logger.info(f"Topic '{topic_name}' created")

    def subscribe(self, topic_name, subscriber: Subscriber):
        with self._lock:
            if topic_name not in self.topics:
                raise ValueError(f"Topic '{topic_name}' does not exist")
            topic = self.topics[topic_name]
        topic.subscribe(subscriber)
        logger.info(f"Subscriber '{subscriber.name}' subscribed to topic '{topic_name}'")

    def unsubscribe(self, topic_name, subscriber: Subscriber):
        with self._lock:
            if topic_name not in self.topics:
                raise ValueError(f"Topic '{topic_name}' does not exist")
            topic = self.topics[topic_name]
        topic.unsubscribe(subscriber)
        logger.info(f"Subscriber '{subscriber.name}' unsubscribed from topic '{topic_name}'")

    def publish(self, topic_name, message: Message):
        with self._lock:
            if topic_name not in self.topics:
                raise ValueError(f"Topic '{topic_name}' does not exist")
            topic = self.topics[topic_name]
        logger.debug(f"Publishing message {message.message_id} to topic '{topic_name}'")
        topic.publish(message)

    def shutdown(self):
        logger.info("Shutting down message broker")
        with self._lock:
            topics = list(self.topics.values())
        for topic in topics:
            topic.shutdown()
        self.executor.shutdown(wait=True)
        logger.info("Message broker shutdown complete")

    def get_topic_dlq(self, topic_name):
        with self._lock:
            if topic_name not in self.topics:
                raise ValueError(f"Topic '{topic_name}' does not exist")
            topic = self.topics[topic_name]
        return topic.get_dlq_messages()
