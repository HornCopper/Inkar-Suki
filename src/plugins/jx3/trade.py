from src.tools.file import get_res_image
from sgtpyutils.encode import basexx
from .jx3 import server_mapping
from src.plugins.help import css
from src.tools.file import write
from src.tools.utils import get_api
from src.tools.generate import generate, get_uuid
import nonebot
import sys

from playwright.async_api import async_playwright
from tabulate import tabulate

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
ASSETS = TOOLS[:-5] + "assets"
CACHE = TOOLS[:-5] + "cache"


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

CACHE_bind = {}
async def check_bind(id: str):
    if id in CACHE_bind:
        return CACHE_bind[id]
    final_url = f"https://helper.jx3box.com/api/wiki/post?type=item&source_id={id}"
    data = await get_api(final_url)
    bind_type = data["data"]["source"]["BindType"]
    if bind_type == None:
        bind_type = 0
    bind_types = ["未知", "不绑定", "装备后绑定", "拾取后绑定"]
    CACHE_bind[id] = bind_types[bind_type]
    return CACHE_bind[id]


async def search_item_info(item_name: str,pageIndex:int=0,pageSize:int=20):
    final_url = f"https://helper.jx3box.com/api/item/search?keyword={item_name}&limit={pageSize}&page={pageIndex+1}"
    box_data = await get_api(final_url)
    items = box_data["data"]["data"]
    if not items:
        return "没有找到该物品哦~"
    space = []
    id = []
    space.append(["序号", "物品ID", "物品名称", "绑定类型", "物品图标"])
    num = 0
    for i in items:
        icon = i["IconID"]
        img_url = f"https://icon.jx3box.com/icon/{icon}.png"
        html_code = f"<img src={img_url}></img>"
        bind_type = await check_bind(i["id"])
        new = [num, i["id"], i["Name"], bind_type, html_code]
        space.append(new)
        id.append(i["id"])
        num = num + 1
    html = "<div style=\"font-family:Custom\">" + \
        tabulate(space, tablefmt="unsafehtml") + "</div>" + css
    final_path = CACHE + "/" + get_uuid() + ".html"
    write(final_path, html)
    img = await generate(final_path, False, "table", False)
    return [id, img]

async def getItemPriceById(id: str, server: str):
    server = server_mapping(server)
    if server == False:
        return "唔……服务器名输入错误。"
    final_url = f"https://next2.jx3box.com/api/item-price/{id}/logs?server={server}"
    data = await get_api(final_url)
    if data["data"]["logs"] == "null":
        return "唔……交易行没有此物品哦~"
    logs = data["data"]["logs"]
    logs.reverse()
    chart = []
    chart.append(["服务器", "日期", "日最高价", "日均价", "日最低价"])
    for i in logs:
        server_ = i["Server"]
        date = i["Date"]
        LowestPrice = convert(i["LowestPrice"])
        AvgPrice = convert(i["AvgPrice"])
        HighestPrice = convert(i["HighestPrice"])
        new = [server_, date, HighestPrice, AvgPrice, LowestPrice]
        chart.append(new)
    html = "<div style=\"font-family:Custom\">" + \
        tabulate(chart, tablefmt="unsafehtml") + "</div>" + css
    final_path = CACHE + "/" + get_uuid() + ".html"
    write(final_path, html)
    img = await generate(final_path, False, "table", False)
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


def convert(price: int):
    if 1 <= price <= 99:  # 铜
        msg = f"{price} 铜"
    elif 100 <= price <= 9999:  # 银
        copper = price % 100
        silver = (price - copper) / 100
        if copper == 0:
            msg = str(int(silver)) + " 银"
        else:
            msg = str(int(silver)) + " 银" + " " + str(int(copper)) + " 铜"
    elif 10000 <= price <= 99999999:  # 金
        copper = price % 100
        silver = ((price - copper) % 10000) / 100
        gold = (price - copper - silver) / 10000
        msg = str(int(gold)) + " 金"
        if str(int(silver)) != "0":
            msg = msg + " " + str(int(silver)) + " 银"
        if str(int(copper)) != "0":
            msg = msg + " " + str(int(copper)) + " 铜"
    elif 100000000 <= price:  # 砖
        copper = price % 100
        silver: int = ((price - copper) % 10000) / 100
        gold = ((price - copper - silver*100) % 100000000) / 10000
        brick = (price - copper - silver*100 - gold*10000) / 100000000
        msg = str(int(brick)) + " 砖"
        if str(int(gold)) != "0":
            msg = msg + " " + str(int(gold)) + " 金"
        if str(int(silver)) != "0":
            msg = msg + " " + str(int(silver)) + " 银"
        if str(int(copper)) != "0":
            msg = msg + " " + str(int(copper)) + " 铜"
    msg = msg.replace("金", f"<img src=\"{goldl}\">").replace("砖", f"<img src=\"{brickl}\">").replace(
        "银", f"<img src=\"{silverl}\">").replace("铜", f"<img src=\"{copperl}\">")
    return msg


prefix = 'data:image/png;base64,'
target_file = ['brickl.png', 'goldl.png', 'silverl.png', 'copperl.png']
target_url = [basexx.base64_encode(get_res_image(x)) for x in target_file]
target_url = [f'{prefix}{x}' for x in target_url]
brickl, goldl, silverl, copperl = target_url
