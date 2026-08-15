"""
Design a Pub/Sub message broker

Core Requirements:
1. Publishers can publish messages to a topic.
2. Subscribers can subscribe to a topic to get messages.
3. Subscribers can unsubscribe to a topic.
4. All subscribers subscribed to a topic, get the message simultaneously.
5. Messages are delivered asynchronously.
6. Multiple topics can be possible.
7. Multiple subscribers per topic is possible.
8. Design should be extendable to later on add ACK, Retry, DLQ, etc
"""

from pub_sub.entities import Message
from pub_sub.broker import MessageBroker
from pub_sub.publisher import Publisher
from pub_sub.examples.services import (
    RestraurantService,
    PaymentService,
    DeliveryService,
    NotificationService,
    AnalyticsService,
    InventoryService,
)
import time
import logging
from uuid import uuid4

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

broker = MessageBroker(max_workers=10)

broker.create_topic("orders")
broker.create_topic("notifications")
broker.create_topic("analytics")

rs = RestraurantService()
ps = PaymentService()
ds = DeliveryService()
ns = NotificationService()
ans = AnalyticsService()
invs = InventoryService()

broker.subscribe("orders", ps)
broker.subscribe("orders", rs)
broker.subscribe("orders", ds)
broker.subscribe("orders", invs)

broker.subscribe("notifications", ns)

broker.subscribe("analytics", ans)

app_publisher = Publisher(broker, "AppPublisher")
backend_publisher = Publisher(broker, "BackendPublisher")

logger.info("=" * 60)
logger.info("Scenario 1: Single order from app")
logger.info("=" * 60)

order_1 = Message(
    str(uuid4()),
    {
        "order_id": 101,
        "restaurant": "Krispy Kreme",
        "amount": 120,
        "user": "Ankit Josh",
    }
)
app_publisher.publish("orders", order_1)

time.sleep(2)

logger.info("=" * 60)
logger.info("Scenario 2: Backend publishes notification")
logger.info("=" * 60)

notif_msg = Message(
    str(uuid4()),
    {
        "type": "order_confirmed",
        "user": "Ankit Josh",
        "message": "Your order has been confirmed!"
    }
)
backend_publisher.publish("notifications", notif_msg)

time.sleep(3)

logger.info("=" * 60)
logger.info("Scenario 3: Multiple publishers to same topic")
logger.info("=" * 60)

order_2 = Message(
    str(uuid4()),
    {
        "order_id": 102,
        "restaurant": "Pizza Hut",
        "amount": 450,
        "user": "John Doe",
    }
)

order_3 = Message(
    str(uuid4()),
    {
        "order_id": 103,
        "restaurant": "Subway",
        "amount": 200,
        "user": "Jane Smith",
    }
)

app_publisher.publish("orders", order_2)
backend_publisher.publish("orders", order_3)

time.sleep(2)

logger.info("=" * 60)
logger.info("Scenario 4: Batch publish to analytics")
logger.info("=" * 60)

analytics_events = [
    Message(str(uuid4()), {"event": "page_view", "page": "/menu"}),
    Message(str(uuid4()), {"event": "add_to_cart", "item_id": 42}),
    Message(str(uuid4()), {"event": "checkout_started"}),
]

app_publisher.publish_batch("analytics", analytics_events)

time.sleep(15)

logger.info("=" * 60)
logger.info("Publisher Stats:")
logger.info(f"{app_publisher.name}: {app_publisher.published_count} messages")
logger.info(f"{backend_publisher.name}: {backend_publisher.published_count} messages")
logger.info("=" * 60)

broker.shutdown()
