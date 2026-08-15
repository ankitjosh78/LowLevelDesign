# Pub-Sub Message Broker

A thread-safe, asynchronous publish-subscribe message broker implementation in Python for learning Low-Level Design (LLD) concepts.

## Features

- **Asynchronous message delivery** using ThreadPoolExecutor
- **Multiple topics** with independent message streams
- **Multiple publishers** can publish to the same topic
- **Multiple subscribers** per topic with concurrent processing
- **Non-blocking retry mechanism** with exponential backoff using scheduled retry queue
- **Dead Letter Queue (DLQ)** for failed messages
- **Thread-safe operations** with proper locking
- **Publisher tracking** with message count metrics
- **Batch publishing** support

## Architecture

```
MessageBroker
├── Topic (orders)
│   ├── Subscribers: [PaymentService, RestaurantService, DeliveryService, InventoryService]
│   └── DeadLetterQueue
├── Topic (notifications)
│   └── Subscribers: [NotificationService]
└── Topic (analytics)
    └── Subscribers: [AnalyticsService]

Publishers
├── AppPublisher
└── BackendPublisher
```

## Core Components

### Entities

- **Message**: Contains `message_id` and `payload`
- **DeliveryContext**: Tracks delivery attempts, status, and errors
- **DeliveryStatus**: Enum with PENDING, ACKNOWLEDGED, FAILED states

### Broker

- **MessageBroker**: Central coordinator managing topics and thread pool
- **Topic**: Manages subscribers and message distribution for a specific topic
- **Publisher**: Publishes messages to topics with tracking
- **Subscriber**: Abstract base class for implementing message consumers

## Usage

### Running the Example

```bash
# From the lld directory
python -m pub_sub.main
```

### Basic Example

```python
from pub_sub.broker import MessageBroker
from pub_sub.publisher import Publisher
from pub_sub.entities import Message
from pub_sub.subscriber import Subscriber
from uuid import uuid4

# Create broker
broker = MessageBroker(max_workers=10)
broker.create_topic("orders")

# Create subscriber
class OrderProcessor(Subscriber):
    def __init__(self):
        super().__init__("OrderProcessor")
    
    def on_message(self, delivery):
        print(f"Processing: {delivery.message.payload}")
        delivery.acknowledge()

# Subscribe
processor = OrderProcessor()
broker.subscribe("orders", processor)

# Publish
publisher = Publisher(broker, "MyPublisher")
message = Message(str(uuid4()), {"order_id": 123, "amount": 100})
publisher.publish("orders", message)

broker.shutdown()
```

### Creating Custom Subscribers

```python
from pub_sub.subscriber import Subscriber
from pub_sub.entities import DeliveryContext

class MyService(Subscriber):
    def __init__(self):
        super().__init__("MyService")
    
    def on_message(self, delivery: DeliveryContext):
        try:
            # Process the message
            payload = delivery.message.payload
            # ... your logic here
            
            # Acknowledge successful processing
            delivery.acknowledge()
        except Exception as e:
            # Let it retry or fail
            delivery.fail(e)
```

## Example Scenarios

The `main.py` demonstrates:

1. **Single publisher to topic** - One order processed by 4 services
2. **Different topics** - Notifications and analytics on separate topics
3. **Multiple publishers to same topic** - AppPublisher and BackendPublisher both publishing orders
4. **Batch publishing** - Multiple analytics events published together

### Testing Exponential Backoff

```bash
python -m pub_sub.examples.retry_demo
```

This demonstrates retry behavior with exponential backoff when a service fails.

## Design Decisions

### Thread Safety

- **Broker & Topic level locks**: Protect shared state (topics dict, subscribers set)
- **DeliveryContext**: No locks needed - each delivery is owned by single execution path
- **DLQ locks**: Separate lock for dead letter queue operations

### Retry Logic

- Configurable `max_attempts` (default: 3)
- **Non-blocking exponential backoff**: Uses scheduled retry queue instead of blocking threads
  - Formula: `base_delay * 2^(attempt - 1)`
  - Example with `base_delay=1.0`: 1s, 2s, 4s, 8s...
- **RetryScheduler**: Dedicated component with min-heap priority queue
  - Separate daemon thread processes retries at scheduled times
  - Worker threads never blocked waiting for retry delays
  - Scales efficiently with thousands of pending retries
- Automatic retry on failure or non-acknowledgment
- Failed messages after max retries go to DLQ
- Each retry tracked in `DeliveryContext`

### Asynchronous Processing

- ThreadPoolExecutor for concurrent message delivery
- Each subscriber processes messages independently
- Non-blocking publish operations
- Callbacks handle retry logic
- Separate retry scheduler thread for delayed retries
- Worker threads stay available for new messages during retry backoff

## API Reference

### MessageBroker

```python
broker = MessageBroker(max_workers=6)
broker.create_topic(topic_name)
broker.subscribe(topic_name, subscriber)
broker.unsubscribe(topic_name, subscriber)
broker.publish(topic_name, message)
broker.get_topic_dlq(topic_name)
broker.shutdown()
```

### Publisher

```python
publisher = Publisher(broker, name="MyPublisher")
publisher.publish(topic_name, message)
publisher.publish_batch(topic_name, messages)
# Access: publisher.published_count
```

### Subscriber

```python
class MySubscriber(Subscriber):
    def __init__(self):
        super().__init__("MySubscriber")
    
    def on_message(self, delivery: DeliveryContext):
        # Process message
        delivery.acknowledge()  # or delivery.fail(error)
```

### DeliveryContext

```python
delivery.message          # The Message object
delivery.delivery_id      # Unique delivery ID
delivery.attempt          # Current attempt number
delivery.max_attempts     # Max retry attempts
delivery.base_delay       # Base delay for exponential backoff
delivery.status           # DeliveryStatus enum
delivery.acknowledge()    # Mark as successful
delivery.fail(error)      # Mark as failed
delivery.increment_attempt()  # Increment retry count
delivery.get_backoff_delay()  # Calculate current backoff delay
```

## Logging

The system uses Python's `logging` module with INFO level by default:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Future Enhancements

- Message persistence
- Priority queues
- Message filtering/routing
- Subscriber groups with load balancing
- Message TTL (Time To Live)
- Metrics and monitoring hooks
- Rate limiting for publishers

## Requirements

- Python 3.10+
- No external dependencies (uses standard library only)

## Project Structure

```
pub_sub/
├── __init__.py
├── broker.py           # MessageBroker implementation
├── entities.py         # Message, DeliveryContext, DeliveryStatus
├── publisher.py        # Publisher implementation
├── subscriber.py       # Subscriber base class
├── topic.py           # Topic management and delivery
├── retry_scheduler.py  # Non-blocking retry scheduler with priority queue
├── main.py            # Example usage
└── examples/
    ├── __init__.py
    ├── services.py    # Example subscriber implementations
    └── retry_demo.py  # Retry mechanism demonstration
```

## Learning Objectives

This implementation demonstrates:

- **Design patterns**: Observer, Publisher-Subscriber, Scheduler
- **Concurrency**: Thread pools, locks, async processing, non-blocking retries
- **Data structures**: Min-heap priority queue for scheduled retries
- **Error handling**: Retries, DLQ, graceful degradation
- **SOLID principles**: Single responsibility, open/closed
- **Scalability**: Non-blocking architecture, efficient resource utilization
- **Extensibility**: Easy to add new subscribers and features

## License

Educational project for LLD learning purposes.
