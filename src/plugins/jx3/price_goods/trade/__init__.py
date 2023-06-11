from src.plugins.help import css
from src.tools.file import write
from src.tools.utils import get_api
from src.tools.generate import generate, get_uuid

from playwright.async_api import async_playwright
from tabulate import tabulate

from .GoodsInfo import GoodsBindType, GoodsInfo, CACHE_goods, flush_cache_goods, check_bind
from .Golds import Gold

from src.tools.dep.server import *
from src.tools.dep.path import *

'''
交易行物品查询。

数据来源@JX3BOX
'''

css_fixed = """
.c-header
{
    display: none;
}
.m-breadcrumb .u-stat
{
    display: none;
}
.c-breadcrumb
{
    display: none;
}
.c-header-inner
{
    display: none;
}
// 别抄啊，用了好久测出来的呢（
// 要抄好歹点个star 然后赞助赞助（狗头）
"""


async def search_item_info(item_name: str, pageIndex: int = 0, pageSize: int = 40):
    final_url = f"https://helper.jx3box.com/api/item/search?keyword={item_name}&limit={pageSize}&page={pageIndex+1}"
    box_data = await get_api(final_url)
    items = box_data["data"]["data"]
    if not items:
        return "没有找到该物品哦~"
    space = []
    query_items = []
    space.append(["序号", "物品ID", "物品名称", "绑定类型", "物品图标"])
    new_goods = False
    for item in items:
        id = item['id']
        if not id in CACHE_goods:
            item['bind_type'] = await check_bind(id)
            CACHE_goods[id] = GoodsInfo(item)
            new_goods = True
        item: GoodsInfo = CACHE_goods[id]
        query_items.append(item)

    query_items.sort(key=lambda x: x.u_popularity)  # 按热门程度排序
    space += [([index] + x.to_row()) for index, x in enumerate(query_items)]

    html = "<div style=\"font-family:Custom\">" + \
        tabulate(space, tablefmt="unsafehtml") + "</div>" + css
    final_path = CACHE + "/" + get_uuid() + ".html"
    write(final_path, html)
    img = await generate(final_path, False, "table", False)
    if new_goods:
        flush_cache_goods()

    return [[i.id for i in query_items], img]


async def getItemPriceById(id: str, server: str, all_ids: list):
    '''
    通过物品id获取交易行价格
    @param id:物品id
    @param server:服务器名称
    @param all_ids:本次选中的所有id。出现过的id应将其人气降1，以更好排序

    @return [image] | str: 正确处理则返回[]，否则返回错误原因
    '''
    server = server_mapping(server)
    if server == False:
        return PROMPT_ServerInvalid
    goods_info: GoodsInfo = CACHE_goods[id] if id in CACHE_goods else GoodsInfo(
    )
    if goods_info.bind_type == GoodsBindType.BindOnPick:
        return "唔……绑定的物品无法在交易行出售哦~"
    final_url = f"https://next2.jx3box.com/api/item-price/{id}/logs?server={server}"
    data = await get_api(final_url)
    logs = data["data"]["logs"]
    if not logs or logs == "null":
        return "唔……交易行没有此物品哦~"
    logs.reverse()
    chart = []
    chart.append(["日期", "日最高价", "日均价", "日最低价"])
    for i in logs:
        date = i["Date"]
        LowestPrice = Gold(i["LowestPrice"])
        AvgPrice = Gold(i["AvgPrice"])
        HighestPrice = Gold(i["HighestPrice"])
        new = [date, HighestPrice, AvgPrice, LowestPrice]
        chart.append(new)
    header_server = f'<div style="font-size:3rem">交易行·{server}</div>'
    goods_info.u_popularity += 10  # 被选中则增加其曝光概率
    header_goods = f'<div style="margin: 0.5rem;font-size:1.8rem;color:{goods_info.color}">物品 {goods_info.name} <img style="vertical-align: middle;width:1.8rem" src="{goods_info.img_url}"/></div>'
    header = f'{header_server}{header_goods}'
    table = tabulate(chart, tablefmt="unsafehtml")
    table = table.replace('<table>', '<table style="margin: auto">')  # 居中显示
    table = f'<div>{table}</div>'  # 居中表格
    html = f'<section style="text-align: center;width:50rem;"><div style=\"font-family:Custom\">{header}{table}</div></section>' + css
    final_path = CACHE + "/" + get_uuid() + ".html"
    write(final_path, html)
    img = await generate(final_path, False, 'section')

    # 本轮已曝光物品，日后曝光率应下调
    for id in all_ids:
        x: GoodsInfo = CACHE_goods[id]
        x.u_popularity -= 1
    flush_cache_goods()
    return [img]


async def getItem(id: str):
    boxdata = await get_api(f"https://helper.jx3box.com/api/wiki/post?type=item&source_id={id}")
    if boxdata["data"]["source"] == None:
        return ["唔……该物品不存在哦~"]
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=0)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(f"https://www.jx3box.com/item/view/{id}")
        await page.add_style_tag(content=css_fixed)
        path = CACHE + "/" + get_uuid() + ".png"
        await page.locator(".c-item-wrapper").first.screenshot(path=path)
        return path


