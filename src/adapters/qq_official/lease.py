"""同机多工作进程共享一个官方 WebSocket 分片连接。"""

import errno
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def websocket_lease(path: Path) -> Iterator[bool]:
    path.parent.mkdir(parents = True, exist_ok = True)
    with path.open("a+b") as lock:
        try:
            if os.name == "nt":
                import msvcrt

                if lock.tell() == 0:
                    lock.write(b"\0")
                    lock.flush()
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            if error.errno not in {errno.EACCES, errno.EAGAIN}:
                raise
            yield False
        else:
            # 文件描述符关闭即释放锁，进程退出或崩溃后其他工作进程也能接管。
            yield True
