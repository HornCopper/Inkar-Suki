from src.tools.generate import generate, get_uuid, async_playwright
from tabulate import tabulate
from src.tools.file import write
from src.plugins.help import css
from src.tools.dep.server import *
from src.tools.dep.path import *
from src.tools.dep.api import *
from ..api import *
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


async def render_items(query_items: list):
    space = []
    space.append(["序号", "物品ID", "物品名称", "绑定类型", "物品图标"])
    space += [([index] + x.to_row()) for index, x in enumerate(query_items)]
    html_table = tabulate(space, tablefmt="unsafehtml")
    html = ""
    html = f"{html}"
    html = f"<div style=\"font-family:Custom\">{html_table}</div>"
    html = f"{html}{css}"
    final_path = CACHE + "/" + get_uuid() + ".html"
    write(final_path, html)
    img = await generate(final_path, False, "table", False)
    return [[i.id for i in query_items], img]


async def render_price(logs: List[GoodsPriceSummary], server: str, goods_info: GoodsInfo):
    chart = []
    chart.append(["日期", "日最高价", "日均价", "日最低价"])
    for i in logs:
        date = i.Date
        LowestPrice = Gold(i.LowestPrice)
        AvgPrice = Gold(i.AvgPrice)
        HighestPrice = Gold(i.HighestPrice)
        new = [date, HighestPrice, AvgPrice, LowestPrice]
        chart.append(new)
    header_server = f'<div style="font-size:3rem">交易行·{server}</div>'
    header_goods = f'<div style="margin: 0.5rem;font-size:1.8rem;color:{goods_info.color}">物品 {goods_info.name} <img style="vertical-align: middle;width:1.8rem" src="{goods_info.img_url}"/></div>'
    header = f'{header_server}{header_goods}'
    table = tabulate(chart, tablefmt="unsafehtml")
    table = table.replace('<table>', '<table style="margin: auto">')  # 居中显示
    table = f'<div>{table}</div>'  # 居中表格
    html = f'<section style="text-align: center;width:50rem;"><div style=\"font-family:Custom\">{header}{table}</div></section>' + css
    final_path = CACHE + "/" + get_uuid() + ".html"
    write(final_path, html)
    img = await generate(final_path, False, 'section')
    return img


async def render_item_img(id: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=0)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(f"https://www.jx3box.com/item/view/{id}")
        await page.add_style_tag(content=css_fixed)
        path = CACHE + "/" + get_uuid() + ".png"
        await page.locator(".c-item-wrapper").first.screenshot(path=path)
        return path
