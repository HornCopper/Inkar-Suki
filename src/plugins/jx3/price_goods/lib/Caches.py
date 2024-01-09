from .GoodsSerializer import *
from .GoodsPrice import *
from .GoodsBase import *
from sgtpyutils.extensions.clazz import dict2obj
from typing import Dict

from src.tools.file import read
from .GoodsBase import GoodsInfo
from .GoodsFullInfo import GoodsInfoFull


def deserilizer_Goods(data): return dict([[x, GoodsInfoFull.from_dict(data[x])] for x in data])


def deserilizer_GoodsSummary(data): return dict(
    [[x, dict2obj(GoodsPriceSummary(), data[x])] for x in data])
def deserilizer_GoodsDetail(data): return dict(
    [[x, dict2obj(GoodsPriceDetail(), data[x])] for x in data])


def serilizer_Goods(obj_dict): return dict([[x, obj_dict[x].to_dict()] for x in obj_dict])


__db=filebase_database.Database


base_goods=f'{bot_path.common_data_full}pvg_trade_goods'
CACHE_GoodsDb=__db(base_goods, serilizer_Goods, deserilizer_Goods)
CACHE_Goods: dict[str, GoodsInfo]=CACHE_GoodsDb.value


__name=f'{base_goods}_price_summary'
CACHE_Goods_PriceSummaryDb=__db(__name, serilizer_Goods, deserilizer_GoodsSummary)
CACHE_Goods_PriceSummary: dict[str, GoodsPriceSummary]=CACHE_Goods_PriceSummaryDb.value


__name=f'{base_goods}_price_detail'
CACHE_Goods_PriceSummaryDb=__db(__name, serilizer_Goods, deserilizer_GoodsDetail)
CACHE_Goods_PriceDetail: dict[str, GoodsPriceDetail]=CACHE_Goods_PriceSummaryDb.value
