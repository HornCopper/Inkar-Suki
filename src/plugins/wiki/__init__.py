from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from src.utils.analyze import check_number
from src.utils.permission import check_permission, denied
from src.utils.database.operation import get_group_settings, set_group_settings
from src.const.prompts import PROMPT

from .wikilib import wiki as wiki_


SimpleWikiMatcher = on_command("wiki", force_whitespace=True, priority=5)


@SimpleWikiMatcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    title = args.extract_plain_text()
    init_api = get_group_settings(str(event.group_id), "wiki")["startwiki"]
    if init_api == "":
        await SimpleWikiMatcher.finish("尚未指定起始Wiki，请尝试使用以下命令进行绑定：\n+setwiki 任意Wiki页面链接")
    info = await wiki_.simple(init_api, title)
    if not isinstance(info, dict):
        return
    if info["status"] == 202:
        msg = ""
        results = info["data"][0]
        state["results"] = results
        state["wiki"] = info["api"]
        for i in range(len(results)):
            msg = msg + "\n" + str(i) + "." + results[i]
        await SimpleWikiMatcher.send(msg[1:])
        return
    elif info["status"] == 201:
        url = info["link"]
        await SimpleWikiMatcher.finish(f"中间Wiki出现错误，请自行重定向至「{title}」：\n{url}")
    elif info["status"] == 200:
        link = info["link"]
        desc = info["desc"]
        final_msg = f"查询到「{title}」：\n{link}{desc}"
        await SimpleWikiMatcher.finish(final_msg)
    elif info["status"] == 301:
        link = info["link"]
        redirect = info["redirect"]
        from_ = redirect[0]
        to_ = redirect[1]
        desc = info["desc"]
        await SimpleWikiMatcher.finish(f"重定向「{from_}」到「{to_}」：\n{link}{desc}")
    elif info["status"] == 404:
        await SimpleWikiMatcher.finish(f"未找到「{title}」。")
    elif info["status"] == 502:
        await SimpleWikiMatcher.finish(info["reason"])

SetWikiMatcher = on_command("setwiki", force_whitespace=True, priority=5)


@SetWikiMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not check_permission(str(event.user_id), 5):
        await SetWikiMatcher.finish(denied(5))
    api = await wiki_.get_api(args.extract_plain_text())
    if api["status"] == 500:
        await SetWikiMatcher.finish("唔……此站点非有效的MediaWiki，请检查后重试~")
    else:
        link = api["data"]
        now = get_group_settings(str(event.group_id), "wiki")
        now["startwiki"] = link
        set_group_settings(str(event.group_id), "wiki", now)
        await SetWikiMatcher.finish("初始Wiki修改成功！")


def check_interwiki_prefix(group, prefix):
    data = get_group_settings(group, "wiki")
    for i in data["interwiki"]:
        if i["prefix"] == prefix:
            return True
    return False


InterWikiManageMatcher = on_command("interwiki", aliases={"iw"}, force_whitespace=True, priority=5)


@InterWikiManageMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, full_argument: Message = CommandArg()):
    if full_argument.extract_plain_text() == "":
        return
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if not group_admin:
        if not check_permission(str(event.user_id), 5):
            await InterWikiManageMatcher.finish(denied(5))
    args = full_argument.extract_plain_text().split(" ")
    if args[0] == "add":
        if len(args) != 3:
            await InterWikiManageMatcher.finish(PROMPT.ArgumentInvalid)
        prefix = args[1]
        if check_interwiki_prefix(str(event.group_id), prefix):
            await InterWikiManageMatcher.finish("唔……该前缀已被使用，请删除或更新此前缀~")
        link = args[2]
        api = await wiki_.get_api(link)
        if api["status"] == 500:
            await InterWikiManageMatcher.finish("唔……此站点非有效的MediaWiki，请检查后重试~")
        api = api["data"]
        new = {"prefix": prefix, "link": api}
        now = get_group_settings(str(event.group_id), "wiki")
        now["interwiki"].append(new)
        set_group_settings(str(event.group_id), "wiki", now)
        site_name = await wiki_.get_site_info(api)
        await InterWikiManageMatcher.finish("成功添加Interwiki：\n" + site_name)
    elif args[0] == "del":
        if len(args) != 2:
            await InterWikiManageMatcher.finish(PROMPT.ArgumentInvalid)
        prefix = args[1]
        if check_interwiki_prefix(str(event.group_id), prefix) is False:
            await InterWikiManageMatcher.finish("唔……该前缀未被使用，请检查后重试~")
        now = get_group_settings(str(event.group_id), "wiki")
        for i in now["interwiki"]:
            if i["prefix"] == prefix:
                now["interwiki"].remove(i)
        set_group_settings(str(event.group_id), "wiki", now)
        await InterWikiManageMatcher.finish("Interwiki移除成功！")
    elif args[0] == "upd":
        if len(args) != 3:
            await InterWikiManageMatcher.finish(PROMPT.ArgumentInvalid)
        prefix = args[1]
        link = args[2] 
        api = await wiki_.get_api(link)
        if api["status"] == 500:
            await InterWikiManageMatcher.finish("唔……此站点非有效的MediaWiki，请检查后重试~")
        api = api["data"]
        if check_interwiki_prefix(str(event.group_id), prefix) is False:
            await InterWikiManageMatcher.finish("唔……该前缀未被使用，请检查后重试~")
        now = get_group_settings(str(event.group_id), "wiki")
        for i in now["interwiki"]:
            if i["prefix"] == prefix:
                i["link"] = api
        set_group_settings(str(event.group_id), "wiki", now)
        site_name = await wiki_.get_site_info(api)
        await InterWikiManageMatcher.finish("成功更新Interwiki：\n" + site_name)

    await InterWikiManageMatcher.finish(PROMPT.ArgumentInvalid)


def get_local_api(group, prefix):
    local_data = get_group_settings(group, "wiki")
    for i in local_data["interwiki"]:
        if i["prefix"] == prefix:
            return i["link"]
    return False


InterWikiSearchMatcher = on_command("iwiki", force_whitespace=True, priority=5)


@InterWikiSearchMatcher.handle()
async def _(state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    search = args.extract_plain_text().split(":")
    if len(search) <= 1:
        await InterWikiSearchMatcher.finish("唔……没有Interwiki前缀，请检查后重试~")
    prefix = search[0]
    api = get_local_api(str(event.group_id), prefix)
    if len(search) == 2:
        title = search[1]
    else:
        search.remove(search[0])
        title = ":".join(search)
    if api is False:
        await InterWikiSearchMatcher.finish("唔……该前缀不存在哦，请检查后重试~")
    info = await wiki_.simple(api, title)
    if not isinstance(info, dict):
        return
    if info["status"] == 202: 
        msg = ""
        results = info["data"][0] 
        state["results"] = results
        state["wiki"] = info["api"] 
        for i in range(len(results)):
            msg = msg + "\n" + str(i) + "." + results[i]
        await SimpleWikiMatcher.send(msg[1:])
    elif info["status"] == 201: 
        url = info["link"] 
        final_title = f"{prefix}:{title}"
        await SimpleWikiMatcher.finish(f"中间Wiki出现错误，请自行重定向至「{final_title}」：\n{url}")
    elif info["status"] == 200: 
        link = info["link"] 
        desc = info["desc"] 
        full_title = prefix+":"+title
        final_msg = f"查询到「{full_title}」：\n{link}{desc}"
        await SimpleWikiMatcher.finish(final_msg)
    elif info["status"] == 301:
        link = info["link"] 
        redirect = info["redirect"]
        from_ = redirect[0]
        to_ = redirect[1]
        desc = info["desc"]
        await SimpleWikiMatcher.finish(f"重定向「{from_}」到「{to_}」：\n{link}{desc}")
    elif info["status"] == 404:
        final_title = f"{prefix}:{title}"
        await SimpleWikiMatcher.finish(f"未找到「{final_title}」。")
    elif info["status"] == 502:
        await SimpleWikiMatcher.finish(info["reason"])


@InterWikiSearchMatcher.got("num", prompt="发送序号以搜索，发送其他内容则取消搜索。")
@SimpleWikiMatcher.got("num", prompt="发送序号以搜索，发送其他内容则取消搜索。")
async def __(state: T_State, num: Message = Arg()):
    num_ = num.extract_plain_text()
    if not check_number(num_):
        await SimpleWikiMatcher.finish(PROMPT.NumberInvalid)
    api = state["wiki"]
    results = state["results"]
    if int(num_) not in range(len(results)):
        await SimpleWikiMatcher.finish(PROMPT.NumberNotExist)
    title = results[int(num_)]
    info = await wiki_.simple(api, title)
    if not isinstance(info, dict):
        return
    link = info["link"]
    desc = info["desc"]
    msg = f"查询到「{title}」：\n{link}{desc}"
    await SimpleWikiMatcher.finish(msg)

