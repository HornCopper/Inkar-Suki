from sgtpyutils.extensions.clazz import dict2obj
from .GoodsBase import *
from .GoodsPrice import *
from .GoodsSerializer import *

cache_file = ASSETS + "/jx3/info_tradegoods.json"
CACHE_Goods = json.loads(read(cache_file))  # 每次重启后从磁盘加载缓存
CACHE_Goods = dict([[x, dict2obj(GoodsInfo(), CACHE_Goods[x])]
                   for x in CACHE_Goods])  # 转换为类


def flush_CACHE_Goods():
    return flush_CACHE_Goods_Common(CACHE_Goods)



cache_file = ASSETS + "/jx3/info_tradegoods_price_summary.json"
CACHE_Goods_PriceSummary = json.loads(read(cache_file))  # 每次重启后从磁盘加载缓存
CACHE_Goods_PriceSummary = dict([[x, dict2obj(GoodsPriceSummary(), CACHE_Goods_PriceSummary[x])]
                                 for x in CACHE_Goods_PriceSummary])  # 转换为类


def flush_CACHE_PriceSummary():
    return flush_CACHE_Goods_Common(CACHE_Goods_PriceSummary)




cache_file = ASSETS + "/jx3/info_tradegoods_price_detail.json"
CACHE_Goods_PriceDetail = json.loads(read(cache_file))  # 每次重启后从磁盘加载缓存
CACHE_Goods_PriceDetail = dict([[x, dict2obj(GoodsPriceDetail(), CACHE_Goods_PriceDetail[x])]
                                for x in CACHE_Goods_PriceDetail])  # 转换为类
# CACHE_Goods_PriceDetail: dict([id , datetime_hour] : GoodsPrice)

def flush_CACHE_PriceDetail():
    return flush_CACHE_Goods_Common(CACHE_Goods_PriceDetail)
