import nonebot
import sys
import time

from tabulate import tabulate
from nonebot.adapters.onebot.v11 import MessageSegment as ms

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
CACHE = TOOLS[:-5] + "cache"

from utils import get_api
from config import Config
from generate import generate, get_uuid
from file import write

from .jx3 import server_mapping

css = """
<style>
            ::-webkit-scrollbar 
            {
                display: none;   
            }
            table 
            { 
                border-collapse: collapse; 
            } 
            table, th, td
            { 
                border: 1px solid rgba(0,0,0,0.05); 
                font-size: 0.8125rem; 
                font-weight: 500; 
            } 
            th, td 
            { 
                padding: 15px; 
                text-align: left; 
            }
            @font-face
            {
                font-family: Custom;
                src: url("customfont");
            }
</style>"""
css = css.replace("customfont",Config.font_path)

async def get_data(server: str, id: str, group: str):
    server = server_mapping(server, group)
    if server == False:
        return ["服务器输入错误，请检查后重试~"]
    final_url = f"https://www.jx3pet.com/api/firework?server={server}&name={id}"
    content = await get_api(final_url)
    if content["data"] == {}:
        return ["唔……该玩家不存在或是没有人炸过烟花哦~"]
    table = []
    table.append(["服务器","烟花","地图","赠送方","接收方","时间"])
    for i in content["data"]:
        server = i["server"]
        firework = i["name"]
        map = i["map"]
        sender = i["sender"]
        rec = i["recipient"]
        timestamp = i["time"]
        time_local = time.localtime(timestamp / 1000)
        dt = time.strftime("%Y年%m月%d日 %H:%M:%S", time_local)
        table.append([server, firework, map, sender, rec, dt])
    output = str(tabulate(table,headers="firstrow",tablefmt="html"))
    html = "<div style=\"font-family:Custom\">" + output + "</div>" + css
    final_path = CACHE + "/" + get_uuid() + ".html"
    write(final_path, html)
    image = await generate(final_path, False, "table")
    if type(image) != type("sb"):
        return [f"唔，帮助文件生成失败了哦~请联系机器人管理员解决此问题，附带以下信息：\n{image}"]
    else:
        return ms.image(image)