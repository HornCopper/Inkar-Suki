import pathlib2
import urllib

def read(Path, default_value: str = "") -> str:
    try:
        with open(Path, mode="r", encoding="utf-8") as cache:
            msg = cache.read()
        return msg
    except FileNotFoundError:
        if default_value == "":
            return "{}"
        with open(Path, mode="w", encoding="utf-8") as cache:
            cache.write(default_value)
        return default_value


def write(Path, sth) -> bool:
    p = pathlib2.Path(Path).parent
    if not p.exists():
        p.mkdir()  # check if not exist
    with open(Path, mode="w", encoding="utf-8") as cache:
        cache.write(sth)
    return True

def get_content_local(path: str) -> str:
    """
    直接获取文件内容。
    """
    with urllib.request.urlopen(path) as f:  
        content = f.read()
        return content