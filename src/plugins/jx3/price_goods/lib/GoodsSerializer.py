from src.tools.dep.api import *
from enum import Enum
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
            o['img_url'] = o.img_url
        elif isinstance(o, GoodsPriceDetail):
            o = o.__dict__
        elif isinstance(o, GoodsPriceSummary):
            o = o.__dict__

        return super().default(o)


def flush_CACHE_Goods_Common(cache_file: str, target_dict: dict):
    d = dict([key, target_dict[key].__dict__] for key in target_dict)
    data = json.dumps(d, cls=GoodsEncoder)
    write(cache_file, data)
