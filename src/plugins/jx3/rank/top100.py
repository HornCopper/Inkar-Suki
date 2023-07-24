import sys
import time

from nonebot.adapters.onebot.v11 import MessageSegment as ms

from src.tools.dep import *


def boss_mapping(boss: str):
    xjd_num = 10369
    wyhl_num = 10907
    if boss in ["西津渡老一", "张景超", "张法雷", "张景超与张法雷", "张法雷与张景超"]:
        return xjd_num
    elif boss in ["西津渡老二", "刘展"]:
        return xjd_num + 1
    elif boss in ["苏凤楼", "西津渡老三", "孤鸿"]:
        return xjd_num + 2
    elif boss in ["韩敬青", "兵刃巫医", "西津渡老四"]:
        return xjd_num + 3
    elif boss in ["藤原佑野", "西津渡老五", "秘藤比丘", "送的"]:
        return xjd_num + 4
    elif boss in ["李重茂", "废帝", "西津渡老六"]:
        return xjd_num + 5
    elif boss in ["时风"]:
        return wyhl_num
    elif boss in ["乐临川"]:
        return wyhl_num + 1
    elif boss in ["牛波"]:
        return wyhl_num + 2
    elif boss in ["和正"]:
        return wyhl_num + 3
    elif boss in ["武云阙", "解兰舟"]:
        return wyhl_num + 4
    elif boss in ["翁幼之"]:
        return wyhl_num + 5
    else:
        return False


async def get_top100(server: str, boss: str, team: str = None):  # 数据来源@JX3BOX
    server = server_mapping(server)
    boss_id = boss_mapping(boss)
    if boss_id == False:
        return "唔……没有找到该boss哦~"
    if not server:
        return PROMPT_ServerNotExist
    final_url = f"https://team.api.jx3box.com/api/team/race/achieve/{boss_id}/top100?server={server}&event_id=6"
    data = await get_api(final_url)
    people = []
    found = False
    if team != None:
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
    else:
        msg = ""
        num = 1
        for i in data["data"]:
            t = i["team_name"]
            l = i["leader"]
            msg = msg + f"{num}. 【{t}】{l}\n"
            num = num + 1
        return msg + "小提示：团牌后方为团长的ID哦~\n使用“+百强 <服务器> <BOSS名称> <团牌>”可以获得更详细的信息。"
    if found == False:
        return "唔……未找到该团，您可以点击下方链接查看该团是否上榜。\nhttps://www.jx3box.com/rank/race/#/"
    people = "、".join(people).replace("\n、", "\n")
    msg = ms.image(team_logo) + f"\n团长：{leader}\n队员：" + \
        people + f"\n开始时间：{start_time}\n通关时间：{finish_time}"
    return msg
