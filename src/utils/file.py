from pathlib import Path
from typing import Literal

from src.utils.typing import overload

def read(path: str) -> str:
    """
    读取文件内容，使用`UTF-8`编码。

    Args:
        path (str): 指向文件的路径。

    Returns:
        file_content (str): 文件内容。**当文件不存在时，值为空字符串`""`。**
    """
    try:
        with open(path, mode="r", encoding="utf-8") as cache:
            msg = cache.read()
        return msg
    except FileNotFoundError:
        return ""

@overload
def write(path: str, content: str, mode: Literal["w"] = "w") -> bool:
    ...

@overload
def write(path: str, content: bytes, mode: Literal["wb"] = "wb") -> bool:
    ...

def write(path: str, content: str | bytes, mode: Literal["w", "wb"] = "w") -> bool:
    """
    向文件写入字符串数据。如果文件不存在则自动创建。

    Args:
        path (str): 写入的文件路径。
        content (str): 写入的内容。
    """
    p = Path(path).parent
    if not p.exists():
        p.mkdir(parents=True)
    with open(path, mode=mode, encoding="utf-8" if mode != "wb" else None) as cache:
        cache.write(content)
    return True