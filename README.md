# Low-Level Design (LLD)

Learning Low-Level Design by implementing classic system design problems in Python. 90% of the code is written by me along with using AI for consulting and guidance.

## Projects

### [Pub-Sub Message Broker](./pub_sub)
Thread-safe, asynchronous message broker with non-blocking retry mechanism and dead letter queue.

**Concepts**: Observer pattern, async processing, priority queues, exponential backoff

### [Rate Limiter](./rate_limiter)
Extensible rate limiter with multiple strategies (Fixed Window, Sliding Window) and per-client configuration.

**Concepts**: Strategy pattern, dependency injection, efficient data structures

## Learning Approach

**Read the requirements** → **Think through your design** → **Identify entities, responsibilities, relationships** → **Implement iteratively**

Each project README contains:
- Core requirements
- Implementation approach
- Design decisions and trade-offs

## Running

```bash
# Pub-Sub
python -m pub_sub.main
python -m pub_sub.examples.retry_demo

# Rate Limiter
python -m rate_limiter.main
```

## Future

- [ ] Parking Lot System
- [ ] Elevator System
- [ ] LRU Cache
- [ ] Task Scheduler
- [ ] URL Shortener