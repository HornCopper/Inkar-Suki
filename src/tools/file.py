import pathlib2
import urllib

def read(Path) -> str:
    try:
        with open(Path, mode="r", encoding="utf-8") as cache:
            msg = cache.read()
        return msg or "{}"
    except Exception as _:
        return "{}"  # 默认返回空对象


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