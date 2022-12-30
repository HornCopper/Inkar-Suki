import sys
import nonebot
import time

from nonebot.adapters.onebot.v11 import MessageSegment as ms

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
ASSETS = TOOLS[:-5] + "assets"
PLUGINS = TOOLS[:-5] + "plugins"
from utils import get_api
from .jx3 import server_mapping

def boss_mapping(boss:str):
    num = 10369
    if boss in ["西津渡老一","张景超","张法雷","张景超与张法雷","张法雷与张景超"]:
        return num
    elif boss in ["西津渡老二","刘展"]:
        return num + 1
    elif boss in ["苏凤楼","西津渡老三","孤鸿"]:
        return num + 2
    elif boss in ["韩敬青","兵刃巫医","西津渡老四"]:
        return num + 3
    elif boss in ["藤原佑野","西津渡老五","秘藤比丘","送的"]:
        return num + 4
    elif boss in ["李重茂","废帝","西津渡老六"]:
        return num + 5
    else:
        return False

async def get_top100(server: str, team: str, boss: str):
    server = server_mapping(server)
    boss_id = boss_mapping(boss)
    if boss_id == False:
        return "唔……没有找到该boss哦~"
    if server == False:
        return "唔……服务器输入错误。"
    final_url = f"https://team.api.jx3box.com/api/team/race/achieve/{boss_id}/top100?server={server}&event_id=6"
    data = await get_api(final_url)
    people = []
    found = False
    for i in data["data"]:
        if i["team_name"] == team:
            found = True
            leader = i["role"]
            team_logo = i["team_logo"]
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i["start_time"]))
            finish_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i["finish_time"]))
            num = 0
            for x in i["teammate"].split(";"):
                add_one = x.split(",")[0]
                if add_one == leader:
                    continue
                people.append(add_one)
                num = num + 1
                if num == 4:
                    people.append("\n")
                    num = 0
    if found == False:
        return "唔……未找到该团，您可以点击下方链接查看该团是否上榜。\nhttps://www.jx3box.com/rank/race/#/"
    people = "、".join(people).replace("\n、","\n")
    msg = ms.image(team_logo) + f"\n团长：{leader}\n队员：" + people + f"\n开始时间：{start_time}\n通关时间：{finish_time}"
    return msg
    