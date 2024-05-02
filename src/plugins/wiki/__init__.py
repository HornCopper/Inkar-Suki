import json

from src.tools.file import read, write
from src.tools.utils import checknumber
from src.tools.permission import checker, error
from src.tools.basic import *

from .wikilib import wiki as wiki_


wiki = on_command("wiki", force_whitespace=True, priority=5)


@wiki.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    title = args.extract_plain_text()
    init_api = json.loads(read(DATA + "/"+str(event.group_id)+"/wiki.json"))["startwiki"]
    if init_api == "":
        await wiki.finish("尚未指定起始Wiki，请尝试使用以下命令进行绑定：\n+setwiki 任意Wiki页面链接")
    info = await wiki_.simple(init_api, title)
    if info["status"] == 202:
        msg = ""
        results = info["data"][0]
        state["results"] = results
        state["wiki"] = info["api"]
        for i in range(len(results)):
            msg = msg + "\n" + str(i) + "." + results[i]
        await wiki.send(msg[1:])
        return
    elif info["status"] == 201:
        url = info["link"]
        await wiki.finish(f"中间Wiki出现错误，请自行重定向至「{title}」：\n{url}")
    elif info["status"] == 200:
        link = info["link"]
        desc = info["desc"]
        final_msg = f"查询到「{title}」：\n{link}{desc}"
        await wiki.finish(final_msg)
    elif info["status"] == 301:
        link = info["link"]
        redirect = info["redirect"]
        from_ = redirect[0]
        to_ = redirect[1]
        desc = info["desc"]
        await wiki.finish(f"重定向「{from_}」到「{to_}」：\n{link}{desc}")
    elif info["status"] == 404:
        await wiki.finish(f"未找到「{title}」。")
    elif info["status"] == 502:
        await wiki.finish(info["reason"])

setwiki = on_command("setwiki", force_whitespace=True, priority=5)


@setwiki.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 5):
        await setwiki.finish(error(5))
    api = await wiki_.get_api(args.extract_plain_text())
    if api["status"] == 500:
        await setwiki.finish("唔……此站点非有效的MediaWiki，请检查后重试~")
    else:
        link = api["data"]
        now = json.loads(read(DATA + "/" + str(event.group_id) + "/wiki.json"))
        now["startwiki"] = link
        write(DATA + "/" + str(event.group_id) + "/wiki.json", json.dumps(now))
        await setwiki.finish("初始Wiki修改成功！")


def check_interwiki_prefix(group, prefix):
    data = json.loads(read(DATA + "/" + group + "/wiki.json"))
    for i in data["interwiki"]:
        if i["prefix"] == prefix:
            return True
    return False


interwiki = on_command("interwiki", aliases={"iw"}, force_whitespace=True, priority=5)


@interwiki.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if not group_admin:
        if not checker(str(event.user_id), 10):
            await interwiki.finish(error(10))
    args = args.extract_plain_text().split(" ")
    if args[0] == "add":
        if len(args) != 3:
            await interwiki.finish(PROMPT_ArgumentInvalid)
        prefix = args[1]
        if check_interwiki_prefix(str(event.group_id), prefix) is True:
            await interwiki.finish("唔……该前缀已被使用，请删除或更新此前缀~")
        link = args[2]
        api = await wiki_.get_api(link)
        if api["status"] == 500:
            await interwiki.finish("唔……此站点非有效的MediaWiki，请检查后重试~")
        api = api["data"]
        new = {"prefix": prefix, "link": api}
        now = json.loads(read(DATA + "/" + str(event.group_id) + "/wiki.json"))
        now["interwiki"].append(new)
        write(DATA + "/" + str(event.group_id) + "/wiki.json", json.dumps(now))
        site_name = await wiki_.get_site_info(api)
        await interwiki.finish("成功添加Interwiki：\n" + site_name)
    elif args[0] == "del":
        if len(args) != 2:
            await interwiki.finish(PROMPT_ArgumentInvalid)
        prefix = args[1]
        if check_interwiki_prefix(str(event.group_id), prefix) is False:
            await interwiki.finish("唔……该前缀未被使用，请检查后重试~")
        now = json.loads(read(DATA + "/" + str(event.group_id) + "/wiki.json"))
        for i in now["interwiki"]:
            if i["prefix"] == prefix:
                now["interwiki"].remove(i)
        write(DATA + "/" + str(event.group_id) + "/wiki.json", json.dumps(now))
        await interwiki.finish("Interwiki移除成功！")
    elif args[0] == "upd":
        if len(args) != 3:
            await interwiki.finish(PROMPT_ArgumentInvalid)
        prefix = args[1]
        link = args[2]
        api = await wiki_.get_api(link)
        if api["status"] == 500:
            await interwiki.finish("唔……此站点非有效的MediaWiki，请检查后重试~")
        api = api["data"]
        if check_interwiki_prefix(str(event.group_id), prefix) is False:
            await interwiki.finish("唔……该前缀未被使用，请检查后重试~")
        now = json.loads(read(DATA + "/"+str(event.group_id)+"/wiki.json"))
        for i in now["interwiki"]:
            if i["prefix"] == prefix:
                i["link"] = api
        write(DATA + "/" + str(event.group_id) + "/wiki.json", json.dumps(now))
        site_name = await wiki_.get_site_info(api)
        await interwiki.finish("成功更新Interwiki：\n" + site_name)

    await interwiki.finish(PROMPT_ArgumentInvalid)


def get_local_api(group, prefix):
    local_data = json.loads(read(DATA + "/" + group + "/wiki.json"))
    for i in local_data["interwiki"]:
        if i["prefix"] == prefix:
            return i["link"]
    return False


iwiki = on_command("iwiki", force_whitespace=True, priority=5)


@iwiki.handle()
async def _(state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    search = args.extract_plain_text().split(":")
    if len(search) <= 1:
        await iwiki.finish("唔……没有Interwiki前缀，请检查后重试~")
    prefix = search[0]
    api = get_local_api(str(event.group_id), prefix)
    if len(search) == 2:
        title = search[1]
    else:
        search.remove(search[0])
        title = ":".join(search)
    if api is False:
        await iwiki.finish("唔……该前缀不存在哦，请检查后重试~")

    info = await wiki_.simple(api, title)
    if info["status"] == 202:
        msg = ""
        results = info["data"][0]
        state["results"] = results
        state["wiki"] = info["api"]
        for i in range(len(results)):
            msg = msg + "\n" + str(i) + "." + results[i]
        await wiki.send(msg[1:])
    elif info["status"] == 201:
        url = info["link"]
        final_title = f"{prefix}:{title}"
        await wiki.finish(f"中间Wiki出现错误，请自行重定向至「{final_title}」：\n{url}")
    elif info["status"] == 200:
        link = info["link"]
        desc = info["desc"]
        full_title = prefix+":"+title
        final_msg = f"查询到「{full_title}」：\n{link}{desc}"
        await wiki.finish(final_msg)
    elif info["status"] == 301:
        link = info["link"]
        redirect = info["redirect"]
        from_ = redirect[0]
        to_ = redirect[1]
        desc = info["desc"]
        await wiki.finish(f"重定向「{from_}」到「{to_}」：\n{link}{desc}")
    elif info["status"] == 404:
        final_title = f"{prefix}:{title}"
        await wiki.finish(f"未找到「{final_title}」。")
    elif info["status"] == 502:
        await wiki.finish(info["reason"])


@iwiki.got("num", prompt="发送序号以搜索，发送其他内容则取消搜索。")
@wiki.got("num", prompt="发送序号以搜索，发送其他内容则取消搜索。")
async def __(state: T_State, num: Message = Arg()):
    num = num.extract_plain_text()
    if not checknumber(num):
        await wiki.finish(PROMPT_NumberInvalid)
    api = state["wiki"]
    results = state["results"]
    if int(num) not in range(len(results)):
        await wiki.finish(PROMPT_NumberNotExist)
    title = results[int(num)]
    info = await wiki_.simple(api, title)
    link = info["link"]
    desc = info["desc"]
    msg = f"查询到「{title}」：\n{link}{desc}"
    await wiki.finish(msg)

