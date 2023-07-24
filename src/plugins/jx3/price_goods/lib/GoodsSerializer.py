from enum import Enum

from src.tools.dep import *

from .GoodsBase import GoodsInfo
from .GoodsPrice import GoodsPriceSummary, GoodsPriceDetail


class GoodsEncoder(json.JSONEncoder):
    def default(self, o) -> str:
        if isinstance(o, Enum):
            return o.value
        elif isinstance(o, dict):
            return o
        return super().default(o)


class GoodsSerializerEncoder(GoodsEncoder):
    def default(self, o) -> str:
        if isinstance(o, GoodsInfo):
            o = o.__dict__
            o["img_url"] = o.img_url
            return o
        elif isinstance(o, GoodsPriceDetail):
            return o.__dict__
        elif isinstance(o, GoodsPriceSummary):
            return o.__dict__

        return super().default(o)


cache_last_update: dict[str, int] = {}


def __check_last_update(key: str, now: int) -> bool:
    v = cache_last_update.get(key) or [0, 0]
    v[1] += 1
    if v[1] > 30:
        return True
    if now - 600 > v[0]:
        return True
    return False


def __update_last_update(key: str, now: int):
    v = cache_last_update.get(key)
    if v is None:
        v = [0, 0]
        cache_last_update[key] = v
    v[0] = now
    v[1] = 0


def flush_CACHE_Goods_Common(cache_file: str, target_dict: dict, ignore_cache_interval: bool = False):
    n = time.time()
    if not ignore_cache_interval:
        if(not __check_last_update(cache_file, n)):
            return
    __update_last_update(cache_file, n)
    d = dict([key, target_dict[key].__dict__ if not type(target_dict[key])
             == dict else target_dict[key]] for key in target_dict)
    data = json.dumps(d, cls=GoodsSerializerEncoder)
    write(cache_file, data)
