from typing import cast, Callable
from nonebot import on_command
from nonebot.params import CommandArg, Arg, RawCommand
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent, GroupUploadNoticeEvent, MessageSegment as ms

from src.const.jx3.kungfu import Kungfu
from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.analyze import Locations, TuilanData, check_number
from src.utils.database.player import search_player
from src.utils.database.attributes import JX3PlayerAttribute

from src.plugins.notice import notice
from src.plugins.jx3.calculator.compare import EquipInfo, get_equip_list
from src.plugins.preferences.app import Preference
from src.plugins.jx3.equip.equip_config import get_equip_image

from .jx3box import JX3BOXCalculator
from .base import FORMATIONS, INCOMES
from .universe import UniversalCalculator
from .rdps import RDPSCalculator
from .jcl_analyze import CQCAnalyze, FALAnalyze, YXCAnalyze

import re
import json
import copy

calc_matcher = on_command("jx3_calculator", aliases={"计算器", "T计算器", "QC计算器", "JC计算器", "TL计算器", "JY计算器"}, priority=5, force_whitespace=True)

@calc_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg(), cmd: str = RawCommand()):
    if args.extract_plain_text() == "":
        matcher.stop_propagation()
        return
    raw_arg = args.extract_plain_text().split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：计算器 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    state["pzid"] = 0
    tag = "TPVE" if cmd[0] == "T" else "DPSPVE"
    if "QC" in cmd:
        tag = "QCPVE"
    if "JC" in cmd:
        tag = "JCPVE"
    if "TL" in cmd:
        tag = "TLPVE"
    if "JY" in cmd:
        tag = "JYPVE"
    if check_number(name):
        instance = await JX3BOXCalculator.with_pzid(int(name))
        if isinstance(instance, str):
            await calc_matcher.finish(instance)
        state["pzid"] = int(name)
    elif name.startswith("g"):
        global_role_id = name[1:]
        if not check_number(global_role_id):
            await calc_matcher.finish("全局玩家ID输入有误，请检查后重试！")
        instance = await UniversalCalculator.with_global_role_id(int(global_role_id), tag)
        if isinstance(instance, str):
            await calc_matcher.finish(instance)
    else:
        server = Server(server, event.group_id).server
        if server is None:
            await calc_matcher.finish(PROMPT.ServerNotExist)
        instance = await UniversalCalculator.with_name(name, server, tag)
        if isinstance(instance, str):
            await calc_matcher.finish(instance)
    income_ver = Preference(event.user_id, "", "").setting("计算器增益")
    formation_ver = Preference(event.user_id, "", "").setting("计算器阵眼")
    income_code = INCOMES[income_ver]
    instance.income_list = income_code
    instance.income_ver = income_ver
    instance.formation_list = FORMATIONS[formation_ver]
    instance.formation_name = formation_ver
    loops = await instance.get_loop()
    if isinstance(loops, str):
        await calc_matcher.finish("该玩家下线时的心法当前尚未实现计算器，可尝试使用指定计算器（如有）或等待该心法支持！")
    state["loops"] = loops
    state["instance"] = instance
    msg = "请选择计算循环！"
    num = 1
    for loop_name in loops:
        msg += f"\n{num}. {loop_name}"
        num += 1
    await calc_matcher.send(msg)

@calc_matcher.got("loop_order")
async def _(event: GroupMessageEvent, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await calc_matcher.finish("循环选择有误，请重新发起命令！")
    loops: dict[str, dict] = state["loops"]
    instance: UniversalCalculator | JX3BOXCalculator = state["instance"]
    if int(num) > len(list(loops)):
        await calc_matcher.finish("超出可选范围，请重新发起命令！")
    loop_code: dict[str, str] = loops[list(loops)[int(num)-1]]
    data = await instance.image(loop_code)
    if state["pzid"] != 0:
        equip_image = ms.image(await get_equip_image(str(state["pzid"])))
        await calc_matcher.send(equip_image)
    await calc_matcher.finish(data)

equip_compare = on_command("jx3_equip_compare", aliases={"装备对比", "T装备对比", "QC装备对比", "JC装备对比", "TL装备对比", "JY装备对比"}, priority=5, force_whitespace=True)

@equip_compare.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg(), cmd: str = RawCommand()):
    if args.extract_plain_text() == "":
        matcher.stop_propagation()
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [2, 3]:
        await equip_compare.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：装备对比 <服务器> <角色名> <装备名>")
    if len(arg) == 2:
        server = None
        name = arg[0]
        equip = arg[1]
    elif len(arg) == 3:
        server = arg[0]
        name = arg[1]
        equip = arg[2]
    server = Server(server, event.group_id).server
    if server is None:
        await equip_compare.finish(PROMPT.ServerNotExist)
    player_data = await search_player(role_name = name, server_name = server)
    if player_data.roleId == "":
        await equip_compare.finish(PROMPT.PlayerNotExist)
    await JX3PlayerAttribute.from_tuilan(player_data.roleId, player_data.serverName, player_data.globalRoleId)
    tag = "TPVE" if cmd[0] == "T" else "DPSPVE"
    if "QC" in cmd:
        tag = "QCPVE"
    if "JC" in cmd:
        tag = "JCPVE"
    if "TL" in cmd:
        tag = "TLPVE"
    if "JY" in cmd:
        tag = "JYPVE"
    instance = await JX3PlayerAttribute.from_database(int(player_data.globalRoleId), tag, False)
    if instance is None:
        await equip_compare.finish(PROMPT.EquipNotFound)
    kungfu_id = instance.kungfu_id # type: ignore
    current_jcl_line = instance.equip_lines # type: ignore
    currnet_dps_data = UniversalCalculator(current_jcl_line, int(str(kungfu_id)))

    income_ver = Preference(event.user_id, "", "").setting("计算器增益")
    formation_ver = Preference(event.user_id, "", "").setting("计算器阵眼")
    income_code = INCOMES[income_ver]
    formation_code = FORMATIONS[formation_ver]

    currnet_dps_data.income_list = income_code
    currnet_dps_data.income_ver = income_ver
    currnet_dps_data.formation_list = formation_code
    currnet_dps_data.formation_name = formation_ver

    equips = await get_equip_list(equip)
    msg = "请从下面选择装备进行对比！"
    num = 1
    for equip in equips:
        msg += f"\n{num}. ({equip.subkind}) {equip.name}\n{equip.quality} {' '.join(equip.attr)}"
        num += 1
    state["equips"] = equips
    state["kungfu_id"] = kungfu_id
    state["current_data"] = currnet_dps_data
    state["current_jcl"] = current_jcl_line
    await equip_compare.send(msg)
    return

@equip_compare.got("equip_index")
async def _(event: GroupMessageEvent, state: T_State, equip_index: Message = Arg()):
    num = equip_index.extract_plain_text()
    if not check_number(num):
        await equip_compare.finish("装备选择有误，请重新发起命令！")
    equips: list[EquipInfo] = state["equips"]
    equip = equips[int(num)-1]
    if int(num) > len(list(equips)):
        await equip_compare.finish("超出可选范围，请重新发起命令！")
    jcl_line: list[list] = copy.deepcopy(state["current_jcl"])
    for each_equip_line in jcl_line:
        # print(each_equip_line)
        # print(Locations.index(equip.location))
        if each_equip_line[0] == Locations.index(equip.location):
            each_equip_line[2] = equip.item_id
            break
    kungfu_id = state["kungfu_id"]
    new_dps_data = UniversalCalculator(jcl_line, int(str(kungfu_id)))

    income_ver = Preference(event.user_id, "", "").setting("计算器增益")
    formation_ver = Preference(event.user_id, "", "").setting("计算器阵眼")
    income_code = INCOMES[income_ver]
    formation_code = FORMATIONS[formation_ver]

    new_dps_data.income_list = income_code
    new_dps_data.income_ver = income_ver
    new_dps_data.formation_list = formation_code
    new_dps_data.formation_name = formation_ver
    state["updated_data"] = new_dps_data
    loops = await new_dps_data.get_loop()
    state["loops"] = loops
    msg = "请选择计算循环！"
    num = 1
    for loop_name in loops:
        msg += f"\n{num}. {loop_name}"
        num += 1
    await equip_compare.send(msg)
    return

@equip_compare.got("loop_order")
async def _(event: GroupMessageEvent, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await equip_compare.finish("循环选择有误，请重新发起命令！")
    loops: dict[str, dict] = state["loops"]
    if int(num) > len(list(loops)):
        await equip_compare.finish("超出可选范围，请重新发起命令！")
    loop_code: dict[str, str] = loops[list(loops)[int(num)-1]]
    old_instance: UniversalCalculator = state["current_data"]
    new_instance: UniversalCalculator = state["updated_data"]
    old_data = await old_instance.calculate(loop_code)
    new_data = await new_instance.calculate(loop_code)
    if not isinstance(old_data, dict) or not isinstance(new_data, dict):
        await equip_compare.finish(cast(str, old_data))
    msg = f"当前DPS：{old_data['damage_per_second']}\n更新DPS：{new_data['damage_per_second']}"
    await equip_compare.finish(msg)


def check_jcl_name(filename: str, prefix: str) -> bool:
    if not filename.startswith(prefix):
        return False
    pattern = re.compile(
        r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-[\u4e00-\u9fff·\d]+(?:\(\d+\))?-[\u4e00-\u9fff·\d]+(?:\(\d+\))?\.jcl$"
    )
    return bool(pattern.match(filename[4:]))

@notice.handle()
async def _(bot: Bot, event: GroupUploadNoticeEvent):
    analyzer: Callable | None = None
    if check_jcl_name(event.file.name, "IKS-"):
        analyzer = RDPSCalculator
    elif check_jcl_name(event.file.name, "CQC-"):
        analyzer = CQCAnalyze
    elif check_jcl_name(event.file.name, "FAL-"):
        analyzer = FALAnalyze
    elif check_jcl_name(event.file.name, "YXC-"):
        analyzer = YXCAnalyze
    else:
        return
    
    if analyzer is not None:
        try:
            url = event.model_dump()["file"]["url"]
        except KeyError:
            file_id = event.model_dump()["file"]["id"]
            bus_id = event.model_dump()["file"]["busid"]
            file_data = await bot.call_api("get_group_file_url", group_id=event.group_id, file_id=file_id, bus_id=bus_id)
            url = file_data["url"]
        try:
            image = await analyzer(event.file.name[4:], url)
            await bot.send_group_msg(group_id=event.group_id, message=Message(image))
        except json.decoder.JSONDecodeError:
            await bot.send_group_msg(group_id=event.group_id, message="啊哦，音卡的服务器目前似乎暂时有些小问题，请稍后再使用JCL分析？")