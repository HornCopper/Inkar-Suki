from src.tools.dep.api import *

cache_file_goods = f"{ASSETS}/jx3/pvx_flower.json"
CACHE_flower: dict = json.loads(read(cache_file_goods)) or {}


def flush_CACHE_flower():
    data = json.dumps(CACHE_flower)
    write(cache_file_goods, data)
