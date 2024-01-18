from typing import TypeVar, Any
import asyncio
import threading
from sgtpyutils.logger import logger
_T = TypeVar('T')


class SyncRunner(threading.Thread):

    def __init__(self, async_task) -> None:
        self.tasks = async_task
        self.semaphore = threading.Semaphore(0)
        self.exception = None
        self.result = None
        super().__init__(daemon=True)

    def run(self):
        # 创建一个新任务方式
        # loop = asyncio.new_event_loop()
        # self.result = loop.run_until_complete(loop.create_task(self.tasks))
        # self.result = asyncio.run()
        # loop.close()

        try:
            self.result = asyncio.run(self.tasks)
        except Exception as ex:
            self.result = None
            logger.warning(f'fail in running{self.tasks}.Exception:{ex}')
            self.exception = ex
        finally:
            self.semaphore.release()
        return super().run()

    @staticmethod
    def as_sync_method(async_method: asyncio.futures.Future[Any, Any, _T]) -> _T:
        x = SyncRunner(async_method)
        x.start()
        x.semaphore.acquire(timeout=30.0)  # 默认最多等待30秒
        if x.exception:
            raise x.exception
        result = x.result
        return result


if __name__ == '__main__':
    async def async_method():
        await asyncio.sleep(10)
        return 1

    print(SyncRunner.as_sync_method(async_method))
