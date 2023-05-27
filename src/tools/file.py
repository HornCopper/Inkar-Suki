import os


def read(Path):
    try:
        cache = open(Path, mode="r", encoding="utf-8")
        msg = cache.read()
        cache.close()
        return msg
    except:
        return False


def write(Path, sth):
    cache = open(Path, mode="w", encoding="utf-8")
    cache.write(sth)
    cache.close()
    return True


path_cur = os.path.dirname(__file__)
path_roow = os.path.join(path_cur, '..')
path_asset = os.path.join(path_roow, 'assets')
path_asset = os.path.realpath(path_asset)

def get_resource_path(path: str) -> str:
    '''
    获取asset目录下的路径
    '''
    return os.path.join(path_asset, path)


def get_resource(path: str) -> bytes:
    '''
    读取asset目录下的文件
    '''
    res = get_resource_path(path)
    with open(res, 'rb') as f:
        return f.read()


def get_res_image(path: str) -> bytes:
    return get_resource(os.path.join('image', path))


def get_res_font(path: str) -> bytes:
    return get_resource(os.path.join('font', path))
