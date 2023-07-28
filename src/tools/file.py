import os
import pathlib2


def read(Path):
    try:
        cache = open(Path, mode="r", encoding="utf-8")
        msg = cache.read()
        cache.close()
        return msg or "{}"
    except:
        return "{}"  # 默认返回空对象


def write(Path, sth):
    p = pathlib2.Path(Path).parent
    if not p.exists():
        p.mkdir()  # check if not exist
    cache = open(Path, mode="w", encoding="utf-8")
    cache.write(sth)
    cache.close()
    return True


path_cur = os.path.dirname(__file__)
path_roow = os.path.join(path_cur, "..")
path_asset = os.path.join(path_roow, "assets")
path_asset = os.path.realpath(path_asset)


def get_resource_path(path: str) -> str:
    """
    获取asset目录下的路径
    """
    return os.path.join(path_asset, path)


def get_resource(path: str) -> bytes:
    """
    读取asset目录下的文件
    """
    res = get_resource_path(path)
    with open(res, "rb") as f:
        return f.read()


def get_res_image(path: str) -> bytes:
    return get_resource(os.path.join("image", path))


def get_res_font(path: str) -> bytes:
    return get_resource(os.path.join("font", path))
