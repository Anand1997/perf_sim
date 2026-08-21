"""
Functional Queue Abstraction (SICP Section 3.3.2).

In SICP, a queue is modeled as a FIFO structure with procedural data abstraction
and message passing. This implementation uses Python's collections.deque for
O(1) amortized queue operations while preserving closure encapsulation and
functional message dispatch.
"""

from collections import deque
from typing import Any, Callable, List, Optional


class Queue:
    """
    Queue computational object supporting SICP message passing and procedural interfaces.
    """

    def __init__(self):
        self._items: deque = deque()

    def is_empty(self) -> bool:
        """Returns True if the queue contains no items."""
        return len(self._items) == 0

    def front(self) -> Any:
        """Returns the front item without removing it."""
        if self.is_empty():
            raise IndexError("FRONT called on an empty queue")
        return self._items[0]

    def insert(self, item: Any) -> "Queue":
        """Appends an item to the rear of the queue."""
        self._items.append(item)
        return self

    def delete(self) -> Any:
        """Pops and returns the front item."""
        if self.is_empty():
            raise IndexError("DELETE! called on an empty queue")
        return self._items.popleft()

    def items(self) -> List[Any]:
        """Returns a list copy of queue items."""
        return list(self._items)

    def size(self) -> int:
        """Returns current queue length."""
        return len(self._items)

    def __call__(self, message: str, *args: Any) -> Any:
        """SICP Message passing dispatch."""
        if message in ("empty?", "is_empty"):
            return self.is_empty()
        elif message == "front":
            return self.front()
        elif message in ("insert!", "insert"):
            if len(args) == 0:
                return self.insert
            return self.insert(args[0])
        elif message in ("delete!", "delete"):
            return self.delete()
        elif message in ("size", "len"):
            return self.size()
        elif message == "items":
            return self.items()
        else:
            raise ValueError(f"Unknown operation -- QUEUE: {message}")

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return not self.is_empty()

    def __repr__(self) -> str:
        return f"Queue({list(self._items)})"


def make_queue() -> Queue:
    """Constructs a new empty Queue (SICP make-queue)."""
    return Queue()


# Procedural interface following SICP conventions
def empty_queue(queue: Any) -> bool:
    """Checks if a queue is empty (SICP empty-queue?)."""
    if hasattr(queue, "is_empty"):
        return queue.is_empty()
    return queue("empty?")


def front_queue(queue: Any) -> Any:
    """Returns the front item of the queue without removing it (SICP front-queue)."""
    if hasattr(queue, "front"):
        return queue.front()
    return queue("front")


def insert_queue(queue: Any, item: Any) -> Any:
    """Inserts an item at the rear of the queue (SICP insert-queue!)."""
    if hasattr(queue, "insert"):
        queue.insert(item)
        return queue
    queue("insert!", item)
    return queue


def delete_queue(queue: Any) -> Any:
    """Removes and returns the front item of the queue (SICP delete-queue!)."""
    if hasattr(queue, "delete"):
        return queue.delete()
    return queue("delete!")
