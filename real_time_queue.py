import asyncio
import time
from collections import deque
from typing import Dict, Any

class RealTimeQueue:
    """
    Real-time information queue for regular/continous data ingestion into the cognitive architecture
    """
    def __init__(self, max_size: int = 100):
        self.queue = deque(maxlen=max_size)
        self.lock = asyncio.Lock()

    async def enqueue(self, item: Dict[str, Any]):
        """
        Enqueue an item into the real-time queue.
        
        :param item: The item to enqueue, should be a dictionary with relevant data.
        """
        async with self.lock:
            self.queue.append(item)

    async def dequeue(self) -> Dict[str, Any]:
        """
        Dequeue an item from the real-time queue.
        
        :return: The dequeued item or None if the queue is empty.
        """
        async with self.lock:
            if self.queue:
                return self.queue.popleft()
            return None
    

    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        :return: True if the queue is empty, False otherwise.
        """
        return len(self.queue) == 0

    def size(self) -> int:
        """
        Get the current size of the queue.
        
        :return: The number of items in the queue.
        """
        return len(self.queue)

    def peek_first(self) -> Dict[str, Any]:
        """
        Access the first item in the queue without removing it.
        
        :return: The first item in the queue or None if the queue is empty.
        """
        if self.queue:
            return self.queue[0]
        return None

    def peek_last(self) -> Dict[str, Any]:
        """
        Access the last item in the queue without removing it.
        
        :return: The last item in the queue or None if the queue is empty.
        """
        if self.queue:
            return self.queue[-1]
        return None