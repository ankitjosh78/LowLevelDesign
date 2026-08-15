from pub_sub.entities import Message, DeliveryContext
from pub_sub.broker import MessageBroker
from pub_sub.publisher import Publisher
from pub_sub.subscriber import Subscriber
import logging
import time
from uuid import uuid4

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class FlakyService(Subscriber):
    def __init__(self, fail_count=2):
        super().__init__("FlakyService")
        self.call_count = 0
        self.fail_count = fail_count

    def on_message(self, delivery: DeliveryContext):
        self.call_count += 1
        logger.info(f"FlakyService called (attempt {self.call_count})")
        
        if self.call_count <= self.fail_count:
            logger.error(f"Simulating failure on attempt {self.call_count}")
            raise Exception(f"Simulated failure #{self.call_count}")
        
        logger.info("Processing successful!")
        delivery.acknowledge()


broker = MessageBroker(max_workers=5)
broker.create_topic("test")

flaky = FlakyService(fail_count=2)
broker.subscribe("test", flaky)

publisher = Publisher(broker, "TestPublisher")

logger.info("=" * 60)
logger.info("Testing Exponential Backoff")
logger.info("Expected delays: 1s (attempt 2), 2s (attempt 3)")
logger.info("=" * 60)

start_time = time.time()
message = Message(str(uuid4()), {"test": "exponential backoff"})
publisher.publish("test", message)

time.sleep(10)

elapsed = time.time() - start_time
logger.info("=" * 60)
logger.info(f"Total time elapsed: {elapsed:.2f}s")
logger.info(f"FlakyService was called {flaky.call_count} times")
logger.info("=" * 60)

broker.shutdown()
