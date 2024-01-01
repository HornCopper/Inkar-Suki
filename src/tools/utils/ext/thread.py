import threading
import time
import asyncio


class SyncRunner(threading.Thread):

    def __init__(self, async_task) -> None:
        self.tasks = async_task
        self.semaphore = threading.Semaphore(0)
        super().__init__(daemon=True)

    def run(self):
        self.result = asyncio.run(self.tasks)
        self.semaphore.release()
        return super().run()

    @staticmethod
    def as_sync_method(async_method):
        x = SyncRunner(async_method)
        x.start()
        x.semaphore.acquire()
        return x.result
