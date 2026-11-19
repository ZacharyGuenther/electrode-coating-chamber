# This file does not work. The idea was to move towards "production ready code"
# that uses test files like this, but I ran out of time.

import time
from queue import Queue
from threading import Thread


class QueueClearer(Thread):
    def __init__(self, queue: Queue[str]) -> None:
        super().__init__(target=self.clear_queue, name="worker", daemon=True)

        self.queue: Queue[str] = queue

    def clear_queue(self) -> None:
        _ = self.queue.get()
        time.sleep(0.05)
