"""FIFO queue for the complete query/download/render/send operation."""
import asyncio
from collections import deque
from dataclasses import dataclass
from typing import Awaitable, Callable


@dataclass(frozen=True)
class Ticket:
    number: int
    ahead: int
    done: asyncio.Future


class SerialCardQueue:
    def __init__(self):
        self._pending = deque()
        self._worker = None
        self._active = False
        self._sequence = 0
        self._closed = False

    def enqueue(self, work: Callable[[], Awaitable[None]]) -> Ticket:
        """Reserve arrival order synchronously, before any network await."""
        if self._closed:
            raise RuntimeError('奇遇名片队列正在关闭，请稍后重试。')
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        # Accepted jobs still run if the requesting matcher is cancelled.
        # Retrieve unobserved exceptions while preserving them for awaiters.
        future.add_done_callback(lambda done: None if done.cancelled() else done.exception())
        self._sequence += 1
        ticket = Ticket(self._sequence, len(self._pending) + int(self._active), future)
        self._pending.append((work, future))
        if self._worker is None:
            self._worker = loop.create_task(self._run(), name='qiyu-card-queue')
        return ticket

    async def _run(self):
        try:
            while self._pending:
                work, future = self._pending.popleft()
                self._active = True
                try:
                    await work()
                except Exception as error:
                    if not future.done():
                        future.set_exception(error)
                else:
                    if not future.done():
                        future.set_result(None)
                finally:
                    self._active = False
        finally:
            self._worker = None

    async def wait(self, ticket: Ticket):
        # Cancelling a waiter must not remove a queued job or cancel its delivery.
        await asyncio.shield(ticket.done)

    async def close(self):
        self._closed = True
        if self._worker is not None:
            await asyncio.shield(self._worker)
