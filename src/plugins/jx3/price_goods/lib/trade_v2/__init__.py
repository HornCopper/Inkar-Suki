import threading

from concurrent.futures.thread import ThreadPoolExecutor
from sgtpyutils.extensions import distinct
from typing import overload, List

from ..GoodsBase import *
from ..GoodsPrice import *
from ..trade import *


async def search_item_info_for_price(item_name: str, server: str, pageIndex: int = 0, pageSize: int = 20):
    """
    搜索物品，并排除拾绑物品及无销售的物品
    @return list[goods],totalCount
    """
    logger.debug(
        f"search_item_info_for_price:{item_name}[{server}]@page:{pageIndex}(pageSize:{pageSize})")
    data = await search_item_info(item_name, pageIndex=0, pageSize=1000)
    if not isinstance(data, List):
        return [data, None]  # 未返回正确数据
    data = [x for x in data if x.bind_type != GoodsBindType.BindOnPick]
    return await get_prices_by_items(data, server, pageIndex, pageSize)


async def get_prices_by_items(data: list, server: str, pageIndex: int = 0, pageSize: int = 20):
    """
    通过物品列表获取其价格
    """
    prices = await get_goods_current_price(data, server)

    current_prices: List[GoodsPriceDetail] = [[x.id, await get_goods_current_detail_price(x.id, server, only_cache=True)] for x in data]
    current_prices_dict = dict([[v[0], v[1]] for v in current_prices])
    result = []
    for x in data:
        if not x.id in prices:
            continue
        x.price = prices[x.id]
        x.current_price = current_prices_dict.get(x.id)
        result.append(x)
    page_start = pageIndex * pageSize
    total = len(result)
    query_items = result[page_start:page_start+pageSize]
    return [query_items, total]


async def get_goods_current_detail_price(id: str, server: str, only_cache: bool = False) -> list:
    """
    获取单个物品当前详细价格
    """
    key = f"{server}:{id}"
    price_detail: GoodsPriceDetail = CACHE_Goods_PriceDetail.get(key)
    if (not price_detail is None) and (time.time() - price_detail.updated < 600):
        return price_detail
    if only_cache:
        return price_detail
    url = f"https://next2.jx3box.com/api/item-price/{id}/detail?server={server}"
    raw_data = await get_api(url)
    if not raw_data.get("code") == 0:
        msg = raw_data.get("msg")
        return f"获取价格失败了：{msg}"
    data = raw_data.get("data") or {}
    prices = data.get("prices") or []
    price_detail = GoodsPriceDetail(prices)
    price_detail.updated_time()
    CACHE_Goods_PriceDetail[key] = price_detail
    flush_CACHE_PriceDetail()
    return price_detail


@overload
async def get_goods_current_price(goods: List[str], server: str) -> dict[str, GoodsPriceSummary]:
    """
    基于id批量加载当日价格
    """
    ...


@overload
async def get_goods_current_price(goods: List[GoodsInfo], server: str) -> dict[str, GoodsPriceSummary]:
    """
    基于商品信息批量加载当日价格
    """
    ...


async def get_goods_current_price(goods, server: str) -> dict:
    if not goods:
        return []
    if isinstance(goods[0], GoodsInfo):
        goods = [x.id for x in goods]
    ids = str.join(",", goods)
    url = f"https://next2.jx3box.com/api/item-price/list?itemIds={ids}&server={server}"
    data = await get_api(url)
    data = data["data"]
    for x in data:
        data[x] = GoodsPriceSummary(data[x])
    return data


def get_goods_unbind():
    goods = [x for x in CACHE_Goods.values() if x.bind_type.value != GoodsBindType.BindOnUse]
    return goods


def get_favoritest_by_top(top: int = 20):
    goods = get_goods_unbind()
    goods.sort(key=lambda x: -x.u_popularity)
    goods = goods[0:top]
    return goods


def get_favoritest_by_predict(predict: callable):
    goods = get_goods_unbind()
    goods.sort(key=lambda x: -x.u_popularity)
    return [x for index, x in enumerate(goods) if predict(index, x)]


class FavoritestGoodsPriceRefreshThread(threading.Thread):
    """
    定时获取热门商品价格
    """

    def __init__(self) -> None:
        self.id = DateTime().getTime()
        super().__init__(daemon=True)

    def run(self) -> None:
        logger.debug(f"{self.getName()}refresh_favoritest_goods_current_price start")
        all_servers = distinct(server_map.values())
        tasks = []
        goods = get_favoritest_by_top(20)
        for server in all_servers:
            for x in goods:
                tasks.append([x.id, server])
        result: List = []
        pool = ThreadPoolExecutor(max_workers=5)

        def run_single(a, b):
            return asyncio.run(get_goods_current_detail_price(a, b))
        while len(tasks):
            x = tasks.pop()
            r = pool.submit(run_single, x[0], x[1])
            result.append(r)
            time.sleep(0.5+random.random())  # 每1秒添加1个任务直到运行完成
        for x in result:
            x.result()
        logger.debug(f"{self.getName()}refresh_favoritest_goods_current_price complete")
        return super().run()
    def getName(self) -> str:
        parent = super().getName()
        return f"{parent}_{self.id}" 

async def refresh_favoritest_goods_current_price():
    '''
    开启一个新的采集线程
    '''
    thread_fav_prices_refresher = FavoritestGoodsPriceRefreshThread()
    thread_fav_prices_refresher.start()

scheduler.add_job(func=refresh_favoritest_goods_current_price,
                  trigger=IntervalTrigger(minutes=60), misfire_grace_time=300)


async def refresh_goods_popularity():
    """
    降低商品人气
    """
    logger.debug("start refresh_goods_popularity")
    def exp(index, x): return abs(x.u_popularity) > 10
    goods = get_favoritest_by_predict(exp)  # 获取所有有一定记录的物品
    for g in goods:
        g.u_popularity *= 0.995  # 每次降低5‰
    flush_CACHE_Goods()
    logger.debug(f"completed refresh_goods_popularity count:{len(goods)}")

scheduler.add_job(func=refresh_goods_popularity,
                  trigger=IntervalTrigger(minutes=60), misfire_grace_time=300)
