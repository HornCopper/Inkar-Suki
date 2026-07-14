import asyncio

from jinja2 import Template
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, Bot
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from src.utils.analyze import check_number
from src.utils.permission import check_permission, denied
from src.utils.database.operation import get_group_settings, set_group_settings
from src.const.prompts import PROMPT
from src.templates import HTMLSourceCode
from src.utils.generate import generate

from ._template import interwiki_table_head, interwiki_table_row
from .wikilib import wiki as wiki_


SimpleWikiMatcher = on_command("wiki", aliases={"iwiki"}, force_whitespace=True, priority=5)


@SimpleWikiMatcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    title = args.extract_plain_text()
    api = None
    lookup_title = title
    if ":" in title:
        prefix, prefixed_title = title.split(":", maxsplit=1)
        local_api = get_local_api(str(event.group_id), prefix)
        if local_api is not False:
            api = local_api
            lookup_title = prefixed_title
    if api is None:
        api = get_group_settings(str(event.group_id), "wiki")["startwiki"]
    if api == "":
        await SimpleWikiMatcher.finish("尚未指定起始Wiki，请尝试使用以下命令进行绑定：\n+setwiki 任意Wiki页面链接")
    info = await wiki_.simple(api, lookup_title)
    if not isinstance(info, dict):
        return
    if info["status"] == 202:
        msg = ""
        results = info["data"][0]
        state["results"] = results
        state["wiki"] = info["api"]
        for i in range(len(results)):
            msg = msg + "\n" + str(i) + "." + results[i]
        await SimpleWikiMatcher.send(
            msg[1:] + "\n发送序号以搜索，发送其他内容则取消搜索。"
        )
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


StartWikiMatcher = on_command("startwiki", force_whitespace=True, priority=5)


@StartWikiMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text():
        return
    api = get_group_settings(str(event.group_id), "wiki")["startwiki"]
    if not api:
        await StartWikiMatcher.finish("当前群尚未设置起始Wiki。")
    site_name = await wiki_.get_site_info(api)
    home_page = await wiki_.get_home_page(api)
    await StartWikiMatcher.finish(f"当前起始Wiki：{site_name}\n首页：{home_page}")


WikiHelpMatcher = on_command("wikihelp", force_whitespace=True, priority=5)


@WikiHelpMatcher.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text():
        return
    await WikiHelpMatcher.finish(
        "Wiki命令帮助：\n"
        "wiki <词条>：查询起始Wiki\n"
        "wiki <前缀:词条>：查询自定义或原生Interwiki\n"
        "startwiki：查看当前起始Wiki\n"
        "setwiki <Wiki页面链接>：设置起始Wiki\n"
        "interwiki list：查看自定义Wiki\n"
        "interwiki add <前缀> <Wiki页面链接>：添加自定义Wiki\n"
        "interwiki del <前缀>：删除自定义Wiki\n"
        "interwiki upd <前缀> <Wiki页面链接>：更新自定义Wiki"
    )

SetWikiMatcher = on_command("setwiki", force_whitespace=True, priority=5)


@SetWikiMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not check_permission(str(event.user_id), "wiki.startwiki.set"):
        await SetWikiMatcher.finish(denied("wiki.startwiki.set"))
    api = await wiki_.get_api(args.extract_plain_text())
    if api["status"] == 500:
        await SetWikiMatcher.finish("唔……此站点非有效的MediaWiki，请检查后重试~")
    else:
        link = api["data"]
        now = get_group_settings(str(event.group_id), "wiki")
        now["startwiki"] = link
        set_group_settings(str(event.group_id), "wiki", now)
        site_name = await wiki_.get_site_info(link)
        await SetWikiMatcher.finish(
            f"初始Wiki修改成功！\n当前Wiki：{site_name}"
        )


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
    args = full_argument.extract_plain_text().split()
    if args[0] == "list":
        if len(args) != 1:
            await InterWikiManageMatcher.finish(PROMPT.ArgumentInvalid)
        records = get_group_settings(str(event.group_id), "wiki")["interwiki"]
        if not records:
            await InterWikiManageMatcher.finish("当前群尚未设置自定义Wiki。")
        site_names = await asyncio.gather(
            *(wiki_.get_site_info(record["link"]) for record in records)
        )
        rows = [
            Template(interwiki_table_row).render(
                prefix=record["prefix"],
                site_name=site_name,
            )
            for record, site_name in zip(records, site_names)
        ]
        html = str(
            HTMLSourceCode(
                application_name="自定义Wiki",
                table_head=interwiki_table_head,
                table_body="".join(rows),
            )
        )
        await InterWikiManageMatcher.finish(
            await generate(html, ".container", segment=True)
        )
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if not group_admin:
        if not check_permission(str(event.user_id), "wiki.interwiki.manage"):
            await InterWikiManageMatcher.finish(denied("wiki.interwiki.manage"))
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


@SimpleWikiMatcher.got("num")
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

