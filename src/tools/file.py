import pathlib2
import urllib

def read(Path):
    try:
        cache = open(Path, mode="r", encoding="utf-8")
        msg = cache.read()
        cache.close()
        return msg or "{}"
    except Exception as _:
        return "{}"  # 默认返回空对象


def write(Path, sth):
    p = pathlib2.Path(Path).parent
    if not p.exists():
        p.mkdir()  # check if not exist
    cache = open(Path, mode="w", encoding="utf-8")
    cache.write(sth)
    cache.close()
    return True

def get_content_local(path: str):
    """
    直接获取文件内容。
    """
    with urllib.request.urlopen(path) as f:  
        content = f.read()
        return content