from pub_sub.entities import DeliveryContext, DeliveryStatus, Message
from pub_sub.subscriber import Subscriber
import threading
import logging

logger = logging.getLogger(__name__)


class Topic:

    def __init__(self, name, shared_executor):
        self.name = name
        self.subscribers: set[Subscriber] = set()
        self.executor = shared_executor
        self.dead_letter_queue: list[DeliveryContext] = []
        self._lock = threading.Lock()
        self._dlq_lock = threading.Lock()

    def subscribe(self, subscriber):
        with self._lock:
            self.subscribers.add(subscriber)

    def unsubscribe(self, subscriber):
        with self._lock:
            self.subscribers.discard(subscriber)

    def _handle_result(self, future, subscriber, delivery):
        exception = future.exception()

        if exception is not None:
            delivery.fail(exception)
            logger.error(
                f"Delivery {delivery.delivery_id} failed for subscriber {subscriber.name}: {exception}"
            )

        if delivery.status == DeliveryStatus.ACKNOWLEDGED:
            logger.info(
                f"Delivery {delivery.delivery_id} acknowledged by {subscriber.name} on attempt {delivery.attempt}"
            )
            return

        if delivery.attempt < delivery.max_attempts:
            delivery.increment_attempt()
            logger.warning(
                f"Retrying delivery {delivery.delivery_id} to {subscriber.name}, attempt {delivery.attempt}"
            )
            self._dispatch(subscriber, delivery)
        else:
            logger.error(
                f"Delivery {delivery.delivery_id} to {subscriber.name} exhausted all retries"
            )
            self._add_to_dlq(delivery)

    def _dispatch(self, subscriber, delivery):
        try:
            future = self.executor.submit(subscriber.on_message, delivery)
            future.add_done_callback(
                lambda f, s=subscriber, d=delivery: self._handle_result(f, s, d)
            )
        except Exception as e:
            logger.error(f"Failed to dispatch message to {subscriber.name}: {e}")
            delivery.fail(e)
            self._add_to_dlq(delivery)

    def _add_to_dlq(self, delivery):
        with self._dlq_lock:
            self.dead_letter_queue.append(delivery)

    def get_dlq_messages(self):
        with self._dlq_lock:
            return list(self.dead_letter_queue)

    def publish(self, message: Message):
        with self._lock:
            subscribers = list(self.subscribers)

        if not subscribers:
            logger.warning(f"No subscribers for topic {self.name}")
            return

        for subscriber in subscribers:
            delivery_context = DeliveryContext(message)
            self._dispatch(subscriber, delivery_context)
