from sgtpyutils.extensions.clazz import dict2obj
from .GoodsBase import *
from .GoodsPrice import *
from .GoodsSerializer import *
from typing import Dict
cache_file_goods = ASSETS + "/jx3/info_tradegoods.json"
CACHE_Goods: Dict[str, GoodsInfo] = json.loads(
    read(cache_file_goods))  # 每次重启后从磁盘加载缓存
CACHE_Goods = dict([[x, dict2obj(GoodsInfo(), CACHE_Goods[x])]
                   for x in CACHE_Goods])  # 转换为类


def flush_CACHE_Goods():
    return flush_CACHE_Goods_Common(cache_file_goods, CACHE_Goods)


cache_file_summary = ASSETS + "/jx3/info_tradegoods_price_summary.json"
CACHE_Goods_PriceSummary: Dict[str, GoodsPriceSummary] = json.loads(
    read(cache_file_summary))  # 每次重启后从磁盘加载缓存
CACHE_Goods_PriceSummary = dict([[x, dict2obj(GoodsPriceSummary(), CACHE_Goods_PriceSummary[x])]
                                 for x in CACHE_Goods_PriceSummary])  # 转换为类


def flush_CACHE_PriceSummary():
    return flush_CACHE_Goods_Common(cache_file_summary, CACHE_Goods_PriceSummary)


cache_file_detail = ASSETS + "/jx3/info_tradegoods_price_detail.json"
CACHE_Goods_PriceDetail: Dict[str, GoodsPriceDetail] = json.loads(
    read(cache_file_detail))  # 每次重启后从磁盘加载缓存
CACHE_Goods_PriceDetail = dict([[x, dict2obj(GoodsPriceDetail(), CACHE_Goods_PriceDetail[x])]
                                for x in CACHE_Goods_PriceDetail])  # 转换为类


def flush_CACHE_PriceDetail():
    return flush_CACHE_Goods_Common(cache_file_detail, CACHE_Goods_PriceDetail)
