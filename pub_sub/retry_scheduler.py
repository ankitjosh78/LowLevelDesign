import heapq
import threading
import time
import logging

logger = logging.getLogger(__name__)


class RetryScheduler:
    def __init__(self):
        self.retry_queue = []
        self.lock = threading.Lock()
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._process_retries, daemon=True)
        self.scheduler_thread.start()

    def schedule_retry(self, retry_after_seconds, callback, subscriber, delivery):
        retry_timestamp = time.time() + retry_after_seconds
        with self.lock:
            heapq.heappush(
                self.retry_queue,
                (retry_timestamp, callback, subscriber, delivery)
            )
            logger.debug(
                f"Scheduled retry for delivery {delivery.delivery_id} "
                f"after {retry_after_seconds}s"
            )

    def _process_retries(self):
        while self.running:
            now = time.time()
            with self.lock:
                while self.retry_queue and self.retry_queue[0][0] <= now:
                    retry_timestamp, callback, subscriber, delivery = heapq.heappop(
                        self.retry_queue
                    )
                    try:
                        callback(subscriber, delivery)
                    except Exception as e:
                        logger.error(f"Error processing retry: {e}")
            time.sleep(0.1)

    def shutdown(self):
        self.running = False
        if self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=2)
