from tabulate import tabulate

from src.tools.basic import *
from src.plugins.help import css
from src.tools.generate import generate, get_uuid

from .top100 import *

async def rank_(type_1: str, type_2: str, server: str, group_id: str):
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    if token is None:
        return [PROMPT_NoToken]
    final_url = f"{Config.jx3.api.url}/view/rank/statistical?token={token}&nickname={bot}&server={server}&table={type_1}&name={type_2}&chrome=1"
    if type_1 == "个人":
        if type_2 not in ["名士五十强", "老江湖五十强", "兵甲藏家五十强", "名师五十强", "阵营英雄五十强", "薪火相传五十强", "庐园广记一百强"]:
            return ["唔……类型不正确，请检查后重试~"]
    elif type_1 == "帮会":
        if type_2 not in ["浩气神兵宝甲五十强", "恶人神兵宝甲五十强", "浩气爱心帮会五十强", "恶人爱心帮会五十强"]:
            return ["唔……类型不正确，请检查后重试~"]
    elif type_1 == "战功":
        if type_2 not in ["赛季恶人五十强", "赛季浩气五十强", "上周恶人五十强", "上周浩气五十强", "本周恶人五十强", "本周浩气五十强"]:
            return ["唔……类型不正确，请检查后重试~"]
    else:
        return ["未知类型，只能是个人/帮会/战功哦！\n提示：试炼榜单的命令已独立。"]
    data = await get_api(final_url)
    if data["code"] == 400:
        return [PROMPT_ArgumentInvalid]
    if data["code"] == 404:
        return ["唔……未收录！"]
    return data["data"]["url"]

async def sl_rank_(server: str, group_id: str, school: str = None):
    if server == "全服":
        # 全服试炼榜单
        final_url = f"{Config.jx3.api.url}/view/rank/server/statistical?table=试炼&name={school}&nickname={bot}"
        data = await get_api(final_url)
        if data["code"] == 400:
            return [PROMPT_ArgumentInvalid]
        if data["code"] == 404:
            return ["唔……未收录！"]
        return data["data"]["url"]
    else:
        # 区服试炼榜单
        final_url = f"{Config.jx3.api.url}/view/rank/statistical?token={token}&nickname={bot}&server={server}&table=试炼&name={school}&chrome=1"
        data = await get_api(final_url)
        if data["code"] == 400:
            return [PROMPT_ArgumentInvalid]
        if data["code"] == 404:
            return ["唔……未收录！"]
        return data["data"]["url"]