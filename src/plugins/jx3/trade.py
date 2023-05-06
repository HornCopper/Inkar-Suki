import nonebot
import sys

from playwright.async_api import async_playwright
from tabulate import tabulate

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
ASSETS = TOOLS[:-5] + "assets"
CACHE = TOOLS[:-5] + "cache"

from src.tools.generate import generate, get_uuid
from src.tools.utils import get_api
from src.tools.file import write

from src.plugins.help import css

from .jx3 import server_mapping

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

async def search_item_info(item_name: str):
    final_url = f"https://helper.jx3box.com/api/item/search?keyword={item_name}&limit=1000"
    box_data = await get_api(final_url)
    if len(box_data["data"]["data"]) == 0:
        return "没有找到该物品哦~"
    space = []
    id = []
    space.append(["序号","物品ID","物品名称","物品图标"])
    num = 0
    for i in box_data["data"]["data"]:
        icon = i["IconID"]
        img_url = f"https://icon.jx3box.com/icon/{icon}.png"
        html_code = f"<img src={img_url}></img>"
        new = [num, i["id"], i["Name"], html_code]
        space.append(new)
        id.append(i["id"])
        num = num + 1
    html = "<div style=\"font-family:Custom\">" + tabulate(space, tablefmt="unsafehtml") + "</div>" + css
    final_path = CACHE + "/" + get_uuid() + ".html"
    write(final_path, html)
    img = await generate(final_path, False, "table", False)
    return [id, img]

async def getItemPriceById(id: str, server: str, group: str = None):
    server = server_mapping(server, group)
    if server == False:
        return "唔……服务器名输入错误。"
    final_url = f"https://next2.jx3box.com/api/item-price/{id}/logs?server={server}"
    data = await get_api(final_url)
    if data["data"]["logs"] == "null":
        return "唔……交易行没有此物品哦~"
    logs = data["data"]["logs"]
    logs.reverse()
    chart = []
    chart.append(["服务器","日期","日最高价","日均价","日最低价"])
    for i in logs:
        server_ = i["Server"]
        date = i["Date"]
        LowestPrice = convert(logs[0]["LowestPrice"])
        AvgPrice = convert(logs[0]["AvgPrice"])
        HighestPrice = convert(logs[0]["HighestPrice"])
        new = [server_, date, HighestPrice, AvgPrice, LowestPrice]
        chart.append(new)
    html = "<div style=\"font-family:Custom\">" + tabulate(chart, tablefmt="unsafehtml") + "</div>" + css
    final_path = CACHE + "/" + get_uuid() + ".html"
    write(final_path, html)
    img = await generate(final_path, False, "table", False)
    return [img]

async def getItem(id: str):
    boxdata = await get_api(f"https://helper.jx3box.com/api/wiki/post?type=item&source_id={id}")
    if boxdata["data"]["source"] == None:
        return ["唔……该物品不存在哦~"]
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless = True, slow_mo = 0)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(f"https://www.jx3box.com/item/view/{id}")
        await page.add_style_tag(content = css_fixed)
        path = CACHE + "/" + get_uuid() + ".png"
        await page.locator(".c-item-wrapper").first.screenshot(path = path)
        return path

def convert(price: int):
    if 1 <= price <= 99: # 铜
        msg = f"{price} 铜"
    elif 100 <= price <= 9999: # 银
        copper = price % 100
        silver = (price - copper) / 100
        if copper == 0:
            msg = str(int(silver)) + " 银" 
        else:
            msg = str(int(silver)) + " 银" + " " + str(int(copper)) + " 铜"
    elif 10000 <= price <= 99999999: # 金
        copper = price % 100
        silver = ((price - copper) % 10000) / 100
        gold = (price - copper - silver) / 10000
        msg = str(int(gold)) + " 金"
        if str(int(silver)) != "0":
            msg = msg + " " + str(int(silver)) + " 银"
        if str(int(copper)) != "0":
            msg = msg + " " + str(int(copper)) + " 铜"
    elif 100000000 <= price: # 砖
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
    msg = msg.replace("金",f"<img src=\"{goldl}\">").replace("砖", f"<img src=\"{brickl}\">").replace("银", f"<img src=\"{silverl}\">").replace("铜", f"<img src=\"{copperl}\">")
    return msg
    
brickl = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAASCAYAAACuLnWgAAAACXBIWXMAAAsTAAALEwEAmpwYAAAGymlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDIgNzkuMTYwOTI0LCAyMDE3LzA3LzEzLTAxOjA2OjM5ICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDIxLTA2LTI3VDExOjI0OjU0KzA4OjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMS0wNy0wN1QwNjoxMjo1MyswODowMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyMS0wNy0wN1QwNjoxMjo1MyswODowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJzUkdCIElFQzYxOTY2LTIuMSIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo5ZGRiZTFmMi01MTA0LWQ0NDItYWQ5NS1iOTcyMTE2YTA3NmEiIHhtcE1NOkRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDpmMzJiMGQxYy00N2Q5LWY1NGItODMzYS1hNjEwZjRiMzQ0NDQiIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDpjOTE4MWRlOC1lN2NjLWRhNDUtYjFhMS03OWM1ZDkxNTdiNjUiPiA8eG1wTU06SGlzdG9yeT4gPHJkZjpTZXE+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJjcmVhdGVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOmM5MTgxZGU4LWU3Y2MtZGE0NS1iMWExLTc5YzVkOTE1N2I2NSIgc3RFdnQ6d2hlbj0iMjAyMS0wNi0yN1QxMToyNDo1NCswODowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTggKFdpbmRvd3MpIi8+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJzYXZlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDoxMjdjOWVkYS1hM2ZmLWZiNDUtYTViMS1mMGZmYzdjNDdhNGEiIHN0RXZ0OndoZW49IjIwMjEtMDctMDdUMDY6MTE6NTYrMDg6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCBDQyAyMDE4IChXaW5kb3dzKSIgc3RFdnQ6Y2hhbmdlZD0iLyIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6OWRkYmUxZjItNTEwNC1kNDQyLWFkOTUtYjk3MjExNmEwNzZhIiBzdEV2dDp3aGVuPSIyMDIxLTA3LTA3VDA2OjEyOjUzKzA4OjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoV2luZG93cykiIHN0RXZ0OmNoYW5nZWQ9Ii8iLz4gPC9yZGY6U2VxPiA8L3htcE1NOkhpc3Rvcnk+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+vCyjFAAAAfBJREFUOMut1E8og3EYwPH3KBzmpvydg2haRKRWUnawiLmsJqU4qOXiTaa3Wasdl4NiViS1HIRprLlYSrTSDnLYCYfFDtSKww5aj+f55bd+r/x53/Grb/udnk/P27tXAgBJ7PNJxpX+bb/Ti03mnjaapF/O53ls5ncIvEH5tm9+UbH33iJQoPCeSMZjXf+CECBbO1YxwE0KuAGLIGeLMfUTpAnJ3ow1LNlrjjHAO8CrDI/XDkhFLOwelFthqr3s4Spus5aMiEB0pZsNp2LLRobBmwsQ+BbSijCAshkkNlxECFBBJzFHSQhtwCEazuOICmozvgTnXA5diGI3AC+bViCXCcDGoplFd7jvhUzCxKL71dEMTFmMz8GFgXFdyJanswjRYOriYEKFJDfrWJALFCH87dGKHIqQbJWKEMW3oPY9BgYQhJtQXm2vcFqp59D5roMhIiRuwTfRjdC5uTitxn/3CQZnOyOIlLGyaRnyWRnCnmYW3e/SMVCcFrDVSrC37pZ1fVY4FJo3qSAazEtFh9hwHiJruhAO4eAoDeeQMigVAbrTcGGTUd0IHXxEVSJEg1UJjwofXUVJCJ38a75SGW4NYbDlm2C5R80w1oibVEv500h4uqRP/VdQ2D8bouECkhGBPyMcuowG+jDnR31aPpDvt7XVCXcJR68AAAAASUVORK5CYII="
goldl = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAASCAYAAACuLnWgAAAACXBIWXMAAAsTAAALEwEAmpwYAAAF+2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDIgNzkuMTYwOTI0LCAyMDE3LzA3LzEzLTAxOjA2OjM5ICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDIxLTA2LTI3VDExOjI0OjU0KzA4OjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMS0wNy0wN1QwNjoxMjo0MCswODowMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyMS0wNy0wN1QwNjoxMjo0MCswODowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJHSU1QIGJ1aWx0LWluIHNSR0IiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6MGJkMzdhNWEtMDhjZC0yOTRjLWFlNmUtOGMzZjQ5MzA5YTBkIiB4bXBNTTpEb2N1bWVudElEPSJhZG9iZTpkb2NpZDpwaG90b3Nob3A6M2E1Y2YwZjMtZmNiNy1hNjRjLTk2ZWMtMzBkZDViMDU1MmVmIiB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6Y2E3OTYzMmQtZGU5My00ZTQ0LTgwNDYtY2JmMzE5ZWZjNjBkIj4gPHhtcE1NOkhpc3Rvcnk+IDxyZGY6U2VxPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0iY3JlYXRlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDpjYTc5NjMyZC1kZTkzLTRlNDQtODA0Ni1jYmYzMTllZmM2MGQiIHN0RXZ0OndoZW49IjIwMjEtMDYtMjdUMTE6MjQ6NTQrMDg6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCBDQyAyMDE4IChXaW5kb3dzKSIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6MGJkMzdhNWEtMDhjZC0yOTRjLWFlNmUtOGMzZjQ5MzA5YTBkIiBzdEV2dDp3aGVuPSIyMDIxLTA3LTA3VDA2OjEyOjQwKzA4OjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoV2luZG93cykiIHN0RXZ0OmNoYW5nZWQ9Ii8iLz4gPC9yZGY6U2VxPiA8L3htcE1NOkhpc3Rvcnk+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+qj+jhgAAAfZJREFUOMvdlE1IG0EYhqdiJC6KkShGRDSoMai0/gTtWrBUAoGooAsWFDyIChahCOLBi4q/lxRLlZSKvQR7CURBiKiQQ88FD3rwLD30mKPHr/NOduIsbIwXDzrw8C0beJ99h8kwImJPDXt5EnMVOQuZxmwWf1/BWQy2u38DJ2MBTjl+siGn5M1rv3s9+NZDgAfucprM8F4j3EAHX0OU+qbT6qSPuEigt2ZY+OgTfB6upx6/68RWwgU3kSWdUrGwBQSDfzdzAkikCCTWdAu/ljqEyFaid9X8TOwblNgJCi7PZwXJ/TDdXkXpLp0SpGIGxTf76PunVtoY8tDerJ8OV3RBMso/LGrQ8nQ35dqud5AgODLjzYog+XM6L0SYqgDIcFXyvrPmKJdE420o/TciwmUjKcEEkEjQCsFoszHiEc9owbPKHjpdGlqoIhkOEUCwZct4OJBN0OKh05U5qk5WHdsZpPT1AmHGt0MWYvxwRMa8WZYnGgTJrQ4xHQWOqrwSUzQhRZfx8awAz2c/DCGSMlXgKnGOyYyckoJXmT8SlxRDNDrgE8EWLuYsIkXwRf3QfNtVrIqmPnhpazqQbQKJ2iQUqBQCTumjJWojLHeJo8Xn0U70RheB/rZ72mq1Y34b1NldQ3kldlcXgJDPZhOHCXu05Nlf9f8B/yrBMSqLm+8AAAAASUVORK5CYII="
silverl = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAASCAYAAACuLnWgAAAACXBIWXMAAAsTAAALEwEAmpwYAAAF+2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDIgNzkuMTYwOTI0LCAyMDE3LzA3LzEzLTAxOjA2OjM5ICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDIxLTA2LTI3VDExOjI0OjU0KzA4OjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMS0wNy0wN1QwNjoxMzoyNiswODowMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyMS0wNy0wN1QwNjoxMzoyNiswODowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJHSU1QIGJ1aWx0LWluIHNSR0IiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6MzE2ZTgxYzQtMDQ2MC02ZDRhLWI0ZTAtMDgzYzEzZDhjNTgwIiB4bXBNTTpEb2N1bWVudElEPSJhZG9iZTpkb2NpZDpwaG90b3Nob3A6ODdmZGNhODktZTgyZC1hMjQ4LWIxZTUtNTlkMTVjN2U4YTFlIiB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6ZjFlMjE3ZDktYWEzOC1lZjQ1LWE1YmItNjZlOTIwYWZkOTk3Ij4gPHhtcE1NOkhpc3Rvcnk+IDxyZGY6U2VxPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0iY3JlYXRlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDpmMWUyMTdkOS1hYTM4LWVmNDUtYTViYi02NmU5MjBhZmQ5OTciIHN0RXZ0OndoZW49IjIwMjEtMDYtMjdUMTE6MjQ6NTQrMDg6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCBDQyAyMDE4IChXaW5kb3dzKSIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6MzE2ZTgxYzQtMDQ2MC02ZDRhLWI0ZTAtMDgzYzEzZDhjNTgwIiBzdEV2dDp3aGVuPSIyMDIxLTA3LTA3VDA2OjEzOjI2KzA4OjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoV2luZG93cykiIHN0RXZ0OmNoYW5nZWQ9Ii8iLz4gPC9yZGY6U2VxPiA8L3htcE1NOkhpc3Rvcnk+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+WEI/qAAAAdRJREFUOMvdlL9LQlEUx99g8SQHx6KIhLCEsB9IUQhSOEQUgg3lIP0gIZJKiCB60A8wghDJECmQfgwVQTUEtoTU0g8amgI3Gx0a/BNO59w6r2doWtDShQ/3DeeeD997370SAEh/jfT/JMWG0SCXIVZklZB0kkHl69BJcl6JrJPNSH+3vT1D2NosI1hejVTQPOR2Pu9trwCB32DvsjJXBNa/To66gWZkPK8EG+8o8z5InEcF8ZiSQ+YlKWDRQsCrkjgKQTysqJAsfxJZmo1tBYF5uDkWXJxEIJ1KQjabFtxen0J8U4ElbO739Ik5sh6Aw92QSrfdVlBipObp1J2QUHOSxLcUVcKCubE+ISDeBcEcCZ6Zp+DBuwZ69khCUHMSsYwFzGfzoEgzNz0qBDSjpLyghNKgSEg4BctIwvB28ZYR2hTUq9gvXBHdUCB5eaiysjgDobWAwO9zC1y9Dpif9qpQIntHE8g6qawUCY1maqwVnR2FBSzRCihtYGqYBA3coKTLiAtyRE/3ZyqUSCugVFjv0K4v+caTyOno2CcZJyG0EhQ8WupNg7xNP5aIA9LLtaaaSl9ro2kZAaazxXJgrquewBJ9vnW/ers+RpUG/XeF//OpfwM0X9GDO5SBFgAAAABJRU5ErkJggg=="
copperl = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAASCAYAAACuLnWgAAAACXBIWXMAAAsTAAALEwEAmpwYAAAF+2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDIgNzkuMTYwOTI0LCAyMDE3LzA3LzEzLTAxOjA2OjM5ICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDIxLTA2LTI3VDExOjI0OjU0KzA4OjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMS0wNy0wN1QwNjoxNDoxMSswODowMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyMS0wNy0wN1QwNjoxNDoxMSswODowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJHSU1QIGJ1aWx0LWluIHNSR0IiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6NWYzZWUxOWMtZDZjOC03NjQ2LWEzM2YtYmI1NWViNWRkNWNiIiB4bXBNTTpEb2N1bWVudElEPSJhZG9iZTpkb2NpZDpwaG90b3Nob3A6YmQzNjFmMmEtOThjMi1hNjQ4LThkZWUtNzcyZGQ5NDdkODI5IiB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6ZGVlNmJiOGMtYmNhOS01MjQ5LThhYjEtNzU2N2M0MTk2NmRlIj4gPHhtcE1NOkhpc3Rvcnk+IDxyZGY6U2VxPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0iY3JlYXRlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDpkZWU2YmI4Yy1iY2E5LTUyNDktOGFiMS03NTY3YzQxOTY2ZGUiIHN0RXZ0OndoZW49IjIwMjEtMDYtMjdUMTE6MjQ6NTQrMDg6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCBDQyAyMDE4IChXaW5kb3dzKSIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6NWYzZWUxOWMtZDZjOC03NjQ2LWEzM2YtYmI1NWViNWRkNWNiIiBzdEV2dDp3aGVuPSIyMDIxLTA3LTA3VDA2OjE0OjExKzA4OjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoV2luZG93cykiIHN0RXZ0OmNoYW5nZWQ9Ii8iLz4gPC9yZGY6U2VxPiA8L3htcE1NOkhpc3Rvcnk+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+Bz8DqwAAAgVJREFUOMu1lc1L40AUwIfS7KZxcSPUEkQ0fqBlDdJoL5WKEFmrUhHiSUEUZBGsn3jx4yIKKlr0oHgqyLK4B2HPC16FveyuRz36D3jxL3i+N3biiBUTxYEfLySZ98tL5k0YALD35umJEkNlrBxpMaLKDLKFp4aQWuRDqfsDSyi5aSg/UgkN+tO6hx3XoMZQv+Mt1lskGgomKbnbp3NkCTHSZ0A6oUOxsuASNczm3O4GkDncz3q4mSYYyVZyUnGVcANJUNCcTMTgz3kO8hsZDh1fXi0+YnWh4ZEIp1b5kqDgM7Kd33E8iYhyJUThyOYiIdMjoVm/ki6qgiSywAgz/ooEOk6l5LLIrlZvqJoXJbrKVrI9Mch9q4PC8ShcXOdhaqwVUiYDs1I5wevDGP86+MEXF2zYO8zwSDj3i6DNj6TwnASvtdPrIJGQFH66sLaeliWdfiS7JCGeq8Su125liaioKIn7kfS2NpdxCSWXJZREgEKeWEgoWqZGkqifJRzBTv5PjTaAouUlC05OHR5z0y0e+QNc2ps2jA+bXsQHdIM0Ywd1MklkEU+M/Dqb4FBiQdLS/ykhpgXqeKwmJyQCuZL+r7osANyCnNfsXZG6KJuXJZRYppTgVbswji9NhvY71YgfPPmAVa+B8UmdV8Oh6Ju3+uL4SLJYhTKGzOHxYPF/wvz8T+4ACwlDiF9TSoMAAAAASUVORK5CYII="

