from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from src.const.jx3.kungfu import Kungfu
from src.utils.analyze import check_number

from .api import get_equips, get_equip_image

EquipRecommendMatcher = on_command("配装", force_whitespace=True, priority=5)

@EquipRecommendMatcher.handle()
async def _(event: GroupMessageEvent, state: T_State, full_argument: Message = CommandArg()):
    if full_argument.extract_plain_text() == "":
        return
    args = full_argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2]:
        await EquipRecommendMatcher.finish("格式错误，请检查命令格式后重试！\n配装 心法 [PVE/PVP]\n或 配装 [PVE/PVP] 心法")
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
        await EquipRecommendMatcher.finish("未找到该心法，请检查后重试！")
    data: list[dict] | str = await get_equips(str(kungfu.id), condition)
    if isinstance(data, str):
        await EquipRecommendMatcher.finish(data)
    else:
        state["d"] = data
        msg = "找到以下配装方案，请选择："
        for n, d in enumerate(data, start=1):
            msg += f"\n{n}. （" + d["pz_author_info"]["display_name"] + "）" + d["title"]
        await EquipRecommendMatcher.send(msg)
        return
    
@EquipRecommendMatcher.got("num")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    n = num.extract_plain_text().strip()
    if not check_number(n):
        await EquipRecommendMatcher.finish("序号错误，请重新发起命令！")
    else:
        data = state["d"]
        equip: dict = data[int(n) - 1]
        equip_id = equip["id"]
        image = ms.image(await get_equip_image(equip_id))
        await EquipRecommendMatcher.finish(image)