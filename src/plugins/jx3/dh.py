import nonebot
import sys

from pathlib import Path

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
ASSETS = TOOLS[:-5] + "assets"

from utils import nodetemp, get_api
from config import Config

async def get_dh(type_: str):
    url = f"https://www.j3dh.com/v1/h/data/hero?ifKnownDaishou=false&exterior={type_}&school=0&figure=0&page=0" # 数据来源 @盆栽蹲号
    data = await get_api(url)
    if data["Code"] != 0:
        return "唔……API访问失败！"
    else:
        node = []
        if data["Result"]["Heros"] == None:
            return "唔……没有获取到任何信息！"
        for i in data["Result"]["Heros"]:
            post = i["PostId"]
            time = i["Time"]
            title = i["Details"]
            thread = i["BigPostId"]
            link = f"http://c.tieba.baidu.com/p/{thread}?pid={post}0&cid=0#{post}"
            msg = f"链接：{link}\n时间：{time}\n详情：{title}"
            node.append(nodetemp("盆栽蹲号查询", Config.bot[0], msg))
            if len(node) == 100:
                break
        if len(node) >= 1:
            return node
        else:
            return "唔……没有获取到任何信息！"