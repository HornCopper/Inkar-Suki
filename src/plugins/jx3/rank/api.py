from src.tools.dep.api import *
from src.tools.dep.server import *
from .top100 import *


async def rank_(type_1: str, type_2: str, server: str, group_id: str):
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    if token == None:
        return [PROMPT_NoToken]
    final_url = f"https://www.jx3api.com/view/rank/excellent?token={token}&robot={bot}&server={server}&table={type_1}&name={type_2}&scale=1"
    if type_1 == "个人":
        if type_2 not in ["名士五十强", "老江湖五十强", "兵甲藏家五十强", "名师五十强", "阵营英雄五十强", "薪火相传五十强", "庐园广记一百强"]:
            return ["唔……类型不正确，请检查后重试~"]
    elif type_1 == "帮会":
        if type_2 not in ["浩气神兵宝甲五十强", "恶人神兵宝甲五十强", "浩气爱心帮会五十强", "恶人爱心帮会五十强"]:
            return ["唔……类型不正确，请检查后重试~"]
    elif type_1 == "战功":
        if type_2 not in ["赛季恶人五十强", "赛季浩气五十强", "上周恶人五十强", "上周浩气五十强", "本周恶人五十强", "本周浩气五十强"]:
            return ["唔……类型不正确，请检查后重试~"]
    elif type_1 == "试炼":
        if type_2 not in ["万花", "七秀", "少林", "纯阳", "天策", "五毒", "唐门", "明教", "苍云", "长歌", "藏剑", "丐帮", "霸刀", "蓬莱", "凌雪", "衍天", "药宗", "刀宗"]:
            return ["唔……门派不正确哦，请检查后重试~"]
    else:
        return ["未知类型，只能是个人/帮会/战功/试炼哦！"]
    data = await get_api(final_url, proxy=proxies)
    if data["code"] == 400:
        return [PROMPT_ArgumentInvalid]
    if data["code"] == 404:
        return ["唔……未收录！"]
    return data["data"]["url"]
