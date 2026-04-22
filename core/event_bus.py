import asyncio
from typing import Optional
from core.schemas import Event


class EventBus:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[Event] = asyncio.Queue()

    async def publish(self, event: Event) -> None:
        await self._queue.put(event)

    async def consume(self, timeout: Optional[float] = None) -> Optional[Event]:
        if timeout is None:
            return await self._queue.get()

        try:
            return await asyncio.wait_for(self._queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def empty(self) -> bool:
        return self._queue.empty()

    def qsize(self) -> int:
        return self._queue.qsize()
