from sgtpyutils.extensions.clazz import get_fields
from typing import List

from src.tools.dep import *

from ..Caches import *


async def search_item_local(item_name: str) -> list:
    v = [CACHE_Goods[x]
         for x in CACHE_Goods if item_name in CACHE_Goods[x].name]
    v = [get_fields(x) for x in v]
    return v


async def search_item_info(item_name: str, pageIndex: int = 0, pageSize: int = 20):
    if not item_name:
        return "请输入物品的名称哦~"
    pageIndex = pageIndex or 0
    final_url = f"https://helper.jx3box.com/api/item/search?keyword={item_name}&limit=1000&page=1"
    box_data = await get_api(final_url)
    items = box_data["data"]["data"]
    if not items:  # 接口请求失败，从本地读取
        items = await search_item_local(item_name)
    if not items:  # 无数据，返回
        return "没有找到该物品哦~"
    query_items: List[GoodsInfo] = []
    new_goods = False
    for item in items:
        id = item["id"]
        if not id in CACHE_Goods:
            item["bind_type"], item["Level"] = await check_bind(id)
            CACHE_Goods[id] = GoodsInfo(item)
            new_goods = True
        item: GoodsInfo = CACHE_Goods[id]
        query_items.append(item)
    if new_goods:
        flush_CACHE_Goods()
    query_items.sort(key=lambda x: -x.priority)  # 按热门程度排序，拾绑的放后面
    page_start = pageIndex * pageSize
    query_items = query_items[page_start:page_start+pageSize]
    return query_items


async def getItemPriceById(id: str, server: str):
    """
    通过物品id获取交易行价格
    @param id:物品id
    @param server:服务器名称

    @return [image] | str: 正确处理则返回[]，否则返回错误原因
    """
    goods_info: GoodsInfo = CACHE_Goods[id] if id in CACHE_Goods else GoodsInfo()
    if goods_info.bind_type == GoodsBindType.BindOnPick:
        return ["唔……绑定的物品无法在交易行出售哦~", None]
    final_url = f"https://next2.jx3box.com/api/item-price/{id}/logs?server={server}"
    data = await get_api(final_url)
    logs = data["data"]["logs"]
    if not logs or logs == "null":
        return ["唔……交易行没有此物品哦~", None]
    logs = [GoodsPriceSummary(x) for x in logs]
    logs.reverse()
    return [logs, goods_info]


async def getItem(id: str):
    boxdata = await get_api(f"https://helper.jx3box.com/api/wiki/post?type=item&source_id={id}")
    if boxdata["data"]["source"] == None:
        return ["唔……该物品不存在哦~"]
    return id


async def update_goods_popularity(target_id: str, all_ids: list):
    """
    更新物品人气，注意物品需要先入库，否则缓存中不存在
    @param all_ids:本次选中的所有id。出现过的id应将其人气降1，以更好排序
    """
    if not CACHE_Goods.get(target_id) is None:
        CACHE_Goods[target_id].u_popularity += 10  # 被选中则增加其曝光概率
    # 本轮已曝光物品，日后曝光率应下调
    for id in all_ids:
        if CACHE_Goods.get(id) is None:
            continue
        x: GoodsInfo = CACHE_Goods[id]
        x.u_popularity -= 1
    flush_CACHE_Goods()
