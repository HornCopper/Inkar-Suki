from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from src.constant.jx3 import getSingleSkill, school_name_aliases

from src.tools.utils.request import get_api
from src.tools.file import read, write
from src.tools.utils.path import ASSETS

from .macro import *

import json
import os

skill = on_command("jx3_skill", aliases={"技能"}, force_whitespace=True, priority=5)


@skill.handle()
async def _(args: Message = CommandArg()):
    """
    查询心法下某技能：

    Example：-技能 莫问 徵
    """
    if args.extract_plain_text() == "":
        return
    info = args.extract_plain_text().split(" ")
    if len(info) != 2:
        await skill.finish("信息不正确哦，只能有2个参数，请检查后重试~")
    else:
        kungfu = info[0]
        skill_ = info[1]
    msg = await getSingleSkill(kungfu, skill_)
    if msg is False:
        await skill.finish("此心法不存在哦，请检查后重试~")
    await skill.finish(msg)

_talent = on_command("jx3_talent", aliases={"奇穴"}, force_whitespace=True, priority=5)


@_talent.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    versions = await get_api("https://data.jx3box.com/talent/index.json")
    if len(arg) not in [2, 3]:
        await _talent.finish("唔……参数不正确哦~")
    if len(arg) == 2:
        kf = arg[0]
        tl = arg[1]
        for i in versions:
            if i["name"].find("体服") != -1:
                continue
            else:
                ver = i["version"]
                break
    else:
        kf = arg[0]
        tl = arg[1]
        ver = arg[2]
        for i in versions:
            if ver == i["name"]:
                ver = i["version"]
    name = school_name_aliases(kf)
    if name is False:
        await _talent.finish("未找到该心法，请检查后重试~")
    if os.path.exists(ASSETS + "/jx3/" + f"{ver}.json") is False:
        final_url = f"https://data.jx3box.com/talent/{ver}.json"
        data = await get_api(final_url)
        write(ASSETS + "/jx3/" + f"v{ver}.json", json.dumps(data, ensure_ascii=False))
    else:
        data = json.loads(read(ASSETS + "/jx3/" + f"{ver}.json"))
    try:
        real_data = data[name]
    except Exception as _:
        await _talent.finish("唔……该赛季没有此心法~")
    for i in range(1, 13):
        for x in range(1, 6):
            try:
                each = real_data[str(i)][str(x)]
            except Exception as _:
                continue
            if each["name"] == tl:
                if each["is_skill"] == 1:
                    special_desc = each["meta"]
                    desc = each["desc"]
                    extend = each["extend"]
                    icon = "https://icon.jx3box.com/icon/" + str(each["icon"]) + ".png"
                    msg = f"第{i}重·第{x}层：{tl}\n" + \
                        ms.image(icon) + f"\n{special_desc}\n{desc}\n{extend}"
                else:
                    desc = each["desc"]
                    icon = "https://icon.jx3box.com/icon/" + str(each["icon"]) + ".png"
                    msg = f"第{i}重·第{x}层：{tl}\n" + ms.image(icon) + f"\n{desc}"
                await _talent.finish(msg)
    await _talent.finish("唔……未找到该奇穴哦~")

macro_ = on_command("jx3_macro_v2", aliases={"宏"}, force_whitespace=True, priority=5)


@macro_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    xf = args.extract_plain_text()
    xf = school_name_aliases(xf)
    if xf is False:
        await macro_.finish("唔……心法输入有误，请检查后重试~")
    data = await get_macro(xf)
    await macro_.finish(data)

# macro_v1 = on_command("jx3_macro", aliases={"宏v1"}, force_whitespace=True, priority=5)


# @macro_v1.handle()
# async def _(event: GroupMessageEvent, args: Message = CommandArg()):
#     if args.extract_plain_text() == "":
#         return
#     xf = aliases(args.extract_plain_text())
#     if xf is False:
#         await macro_v1.finish("唔……心法输入有误，请检查后重试~")
#     data = await get_api(f"{Config.jx3.api.url}/data/school/macro?name={xf}&token={token}")
#     data = data["data"]["context"]
#     await macro_v1.finish(data)
