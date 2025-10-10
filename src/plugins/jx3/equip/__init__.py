from nonebot import on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from src.const.prompts import PROMPT
from src.const.jx3.kungfu import Kungfu
from src.utils.analyze import check_number

from .equip_config import get_equips, get_equip_image
from .equip_find import get_equip_info, get_equip_info_image

referenced_equip_matcher = on_command("jx3_pz", aliases={"配装"}, force_whitespace=True, priority=5)

@referenced_equip_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, full_argument: Message = CommandArg()):
    if full_argument.extract_plain_text() == "":
        return
    args = full_argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2]:
        await referenced_equip_matcher.finish("格式错误，请检查命令格式后重试！\n配装 心法 [PVE/PVP]\n或 配装 [PVE/PVP] 心法")
    condition = []
    classic = ["PVE", "PVP"]
    if len(args) == 2:
        if args[0].upper() in classic:
            kungfu = Kungfu(args[1])
            condition.append(args[0].upper())
        else:
            kungfu = Kungfu(args[0])
            condition.append(args[1].upper())
    elif len(args) == 1:
        kungfu = Kungfu(args[0])
    if kungfu.name is None or kungfu.name.endswith("·悟"):
        await referenced_equip_matcher.finish("未找到该心法，请检查后重试！")
    data: list[dict] | str = await get_equips(str(kungfu.id), condition)
    if isinstance(data, str):
        await referenced_equip_matcher.finish(data)
    else:
        state["d"] = data
        msg = "找到以下配装方案，请选择："
        for n, d in enumerate(data, start=1):
            msg += f"\n{n}. （" + d["pz_author_info"]["display_name"] + "）" + d["title"]
        await referenced_equip_matcher.send(msg)
        return
    
@referenced_equip_matcher.got("num")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    n = num.extract_plain_text().strip()
    if not check_number(n):
        await referenced_equip_matcher.finish("序号错误，请重新发起命令！")
    else:
        data = state["d"]
        equip: dict = data[int(n) - 1]
        equip_id = equip["id"]
        image = ms.image(await get_equip_image(equip_id))
        await referenced_equip_matcher.finish(image)

equip_find_matcher = on_command("jx3_equip_find", aliases={"装备"}, priority=5, force_whitespace=True)

@equip_find_matcher.handle()
async def _(matcher: Matcher, state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    equip_name = args.extract_plain_text().strip()
    if equip_name == "":
        matcher.stop_propagation()
        return
    results = await get_equip_info(equip_name)
    if isinstance(results, str):
        await equip_find_matcher.finish(results)
    if len(results) == 1:
        equip_data = results[0][1]
        image = await get_equip_info_image(equip_data)
        await equip_find_matcher.finish(image)
    else:
        num = 1
        msg = "请从下方选择装备："
        state["equip_data"] = results
        for each_equip, equip_data in results:
            msg += f"\n{num}. {each_equip}"
            num += 1
        await equip_find_matcher.send(msg)
        return

@equip_find_matcher.got("num")
async def _(state: T_State, event: GroupMessageEvent, num: Message = Arg()):
    equip_num = num.extract_plain_text().strip()
    if not check_number(equip_num):
        await equip_find_matcher.finish(PROMPT.NumberInvalid)
    if int(equip_num) > len(state["equip_data"]):
        await equip_find_matcher.finish(PROMPT.NumberNotExist)
    equip_data = state["equip_data"][int(equip_num)-1][1]
    image = await get_equip_info_image(equip_data)
    await equip_find_matcher.finish(image)