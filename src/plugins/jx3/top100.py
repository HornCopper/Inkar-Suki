import sys
import nonebot
import time

from nonebot.adapters.onebot.v11 import MessageSegment as ms

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
ASSETS = TOOLS[:-5] + "assets"
PLUGINS = TOOLS[:-5] + "plugins"
from utils import get_api

async def get_top100(server: str, team: str):
    final_url = f"https://team.api.jx3box.com/api/team/race/achieve/10369/top100?server={server}&event_id=6"
    data = await get_api(final_url)
    people = []
    found = False
    for i in data["data"]:
        if i["team_name"] == team:
            found = True
            team_logo = i["team_logo"]
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i["start_time"]))
            finish_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i["finish_time"]))
            num = 0
            for x in i["teammate"].split(";"):
                people.append(x.split(",")[0])
                num = num + 1
                if num == 4:
                    people.append("\n")
                    num = 0
            leader = i["role"]
    if found == False:
        return "唔……未找到该团，您可以点击下方链接查看该团是否上榜。\nhttps://www.jx3box.com/rank/race/#/"
    people = "、".join(people).replace("\n、","\n")
    msg = ms.image(team_logo) + f"\n团长：{leader}\n队员：" + people + f"开始时间：{start_time}\n通关时间：{finish_time}"
    return msg
    