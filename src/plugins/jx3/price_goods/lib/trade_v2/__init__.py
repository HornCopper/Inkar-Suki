from typing import overload, List
from ..GoodsBase import *
from ..GoodsPrice import *
from ..trade import *


async def search_item_info_for_price(item_name: str, server: str, pageIndex: int = 0, pageSize: int = 20):
    '''
    搜索物品，并排除拾绑物品及无销售的物品
    @return list[goods],totalCount
    '''
    data = await search_item_info(item_name, pageIndex=0, pageSize=1000)
    if not isinstance(data, List):
        return [data, None]  # 未返回正确数据
    data = [x for x in data if x.bind_type != GoodsBindType.BindOnPick]
    prices = await get_goods_current_price(data, server)
    result = []
    for x in data:
        if x.id in prices:
            x.price = prices[x.id]
            result.append(x)
    page_start = pageIndex * pageSize
    total = len(result)
    query_items = result[page_start:page_start+pageSize]
    return [query_items, total]


async def get_goods_current_detail_price(id: str, server: str) -> list:
    '''
    获取单个物品当前详细价格
    '''
    url = f'https://next2.jx3box.com/api/item-price/{id}/detail?server={server}'
    raw_data = await get_api(url)
    if not raw_data.get('code') == 0:
        return f'获取价格失败了：{raw_data.get("msg")}'
    data = raw_data.get('data') or {}
    prices = data.get('prices') or []
    price_detail = GoodsPriceDetail(prices)
    return price_detail


@overload
async def get_goods_current_price(goods: List[str], server: str) -> List[dict]:
    '''
    基于id批量加载当日价格
    '''
    ...


@overload
async def get_goods_current_price(goods: List[GoodsInfo], server: str) -> List[GoodsInfo]:
    '''
    基于商品信息批量加载当日价格
    '''
    ...


async def get_goods_current_price(goods, server: str) -> dict:
    if not goods:
        return []
    if isinstance(goods[0], GoodsInfo):
        goods = [x.id for x in goods]
    ids = str.join(',', goods)
    url = f'https://next2.jx3box.com/api/item-price/list?itemIds={ids}&server={server}'
    data = await get_api(url)
    data = data['data']
    for x in data:
        data[x] = GoodsPriceSummary(data[x])
    return data
