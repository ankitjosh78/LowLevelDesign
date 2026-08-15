from pub_sub.entities import DeliveryContext
from pub_sub.subscriber import Subscriber
import time
import logging

logger = logging.getLogger(__name__)


class RestraurantService(Subscriber):
    def __init__(self):
        super().__init__("RestaurantService")

    def process(self, message):
        logger.info(f"Processing order for restaurant. Message: {message.message_id}")
        time.sleep(5)
        logger.info(f"Restaurant processing complete. Message: {message.message_id}")

    def on_message(self, delivery: DeliveryContext):
        logger.info("Order accepted by restaurant")
        self.process(delivery.message)
        delivery.acknowledge()
        logger.info("Order prepared by restaurant")


class PaymentService(Subscriber):
    def __init__(self):
        super().__init__("PaymentService")

    def process(self, message):
        logger.info(f"Processing payment. Message: {message.message_id}")
        time.sleep(1)
        logger.info(f"Payment processing complete. Message: {message.message_id}")

    def on_message(self, delivery: DeliveryContext):
        logger.info("Payment received")
        self.process(delivery.message)
        delivery.acknowledge()
        logger.info("Payment confirmed")


class DeliveryService(Subscriber):
    def __init__(self):
        super().__init__("DeliveryService")

    def process(self, message):
        logger.info(f"Matching delivery partner. Message: {message.message_id}")
        time.sleep(10)
        logger.info(f"Delivery partner matched. Message: {message.message_id}")

    def on_message(self, delivery: DeliveryContext):
        logger.info("Delivery search started")
        self.process(delivery.message)
        delivery.acknowledge()
        logger.info("Delivery partner found")


class NotificationService(Subscriber):
    def __init__(self):
        super().__init__("NotificationService")

    def process(self, message):
        logger.info(f"Sending notifications. Message: {message.message_id}")
        time.sleep(2)
        logger.info(f"Notifications sent. Message: {message.message_id}")

    def on_message(self, delivery: DeliveryContext):
        logger.info("Notification triggered")
        self.process(delivery.message)
        delivery.acknowledge()
        logger.info("User notified")


class AnalyticsService(Subscriber):
    def __init__(self):
        super().__init__("AnalyticsService")

    def process(self, message):
        logger.info(f"Recording analytics. Message: {message.message_id}")
        time.sleep(1)
        logger.info(f"Analytics recorded. Message: {message.message_id}")

    def on_message(self, delivery: DeliveryContext):
        logger.info("Analytics event captured")
        self.process(delivery.message)
        delivery.acknowledge()
        logger.info("Analytics updated")


class InventoryService(Subscriber):
    def __init__(self):
        super().__init__("InventoryService")

    def process(self, message):
        logger.info(f"Updating inventory. Message: {message.message_id}")
        time.sleep(3)
        logger.info(f"Inventory updated. Message: {message.message_id}")

    def on_message(self, delivery: DeliveryContext):
        logger.info("Inventory check started")
        self.process(delivery.message)
        delivery.acknowledge()
        logger.info("Inventory adjusted")
