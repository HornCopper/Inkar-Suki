from typing import cast
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
from src.utils.database.attributes import AttributeParser, AttributesRequest
from src.plugins.notice import notice
from src.plugins.jx3.calculator.compare import EquipInfo, get_equip_list
from src.plugins.jx3.calculator.calc_zixiagong import ZixiagongCalculator
from src.plugins.preferences.app import Preference
from src.plugins.jx3.equip.api import get_equip_image
from src.plugins.jx3.calculator.jx3box import JX3BOXCalculator

from .calc_yinlongjue import LingxueCalculator
# from .wf import WufangCalculator
# from .bxj import BingxinjueCalculator
from .calc_taixujianyi import TaixujianyiCalculator
# from .calc_tielaolv import TielaolvCalculator
# from .calc_mingzunliuliti import MingzunliulitiCalculator
# from .calc_tieguyi import TieguyiCalculator
# from .calc_xisuijing import XisuijingCalculator
# from .calc_fenyingshengjue import FenyingshengjueCalculator
# from .calc_fenshanjin import FenshanjinCalculator

from .base import FORMATIONS, INCOMES
from .universe import UniversalCalculator
# from .lhj import LinghaijueCalculator
# from .mw import MowenCalculator
# from .dj import DujingCalculator
# from .baj import BeiaojueCalculator
from .rdps import RDPSCalculator
from .cqc import CQCAnalyze

import re
import json
import copy

yinlongjue_calc_matcher = on_command("jx3_calculator_lyj", aliases={"凌雪计算器"}, priority=5, force_whitespace=True)

@yinlongjue_calc_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        matcher.stop_propagation()
        return
    raw_arg = args.extract_plain_text().split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await yinlongjue_calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：凌雪计算器 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await yinlongjue_calc_matcher.finish(PROMPT.ServerNotExist)
    instance = await LingxueCalculator.with_name(name, server, "DPSPVE")
    if isinstance(instance, str):
        await yinlongjue_calc_matcher.finish(instance)
    loops = await instance.get_loop()
    state["full_income"] = len(raw_arg) > len(arg)
    state["loops"] = loops
    state["instance"] = instance
    msg = "请选择计算循环！"
    num = 1
    for loop_name in loops:
        msg += f"\n{num}. {loop_name}"
        num += 1
    await yinlongjue_calc_matcher.send(msg)

@yinlongjue_calc_matcher.got("loop_order")
async def _(event: GroupMessageEvent, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await yinlongjue_calc_matcher.finish("循环选择有误，请重新发起命令！")
    loops: dict[str, dict] = state["loops"]
    full_income: bool = state["full_income"]
    instance: LingxueCalculator = state["instance"]
    if int(num) > len(list(loops)):
        await yinlongjue_calc_matcher.finish("超出可选范围，请重新发起命令！")
    loop_code: dict[str, str] = loops[list(loops)[int(num)-1]]
    data = await instance.image(loop_code, full_income)
    await yinlongjue_calc_matcher.finish(data)

calc_matcher = on_command("jx3_calculator", aliases={"计算器", "T计算器"}, priority=5, force_whitespace=True)

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
    if check_number(name):
        instance = await JX3BOXCalculator.with_pzid(int(name))
        if isinstance(instance, str):
            await calc_matcher.finish(instance)
        state["pzid"] = int(name)
    else:
        server = Server(server, event.group_id).server
        if server is None:
            await calc_matcher.finish(PROMPT.ServerNotExist)
        instance = await UniversalCalculator.with_name(name, server, "TPVE" if cmd[0] == "T" else "DPSPVE")
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

equip_compare = on_command("jx3_equip_compare", aliases={"装备对比", "T装备对比"}, priority=5, force_whitespace=True)

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
    instance = await AttributesRequest.with_name(server, name)
    if not instance:
        await equip_compare.finish(PROMPT.PlayerNotExist)
    equip_data = instance.get_equip("TPVE" if cmd[0] == "T" else "DPSPVE")
    if isinstance(equip_data, bool):
        await equip_compare.finish(PROMPT.PlayerNotExist if equip_data else PROMPT.EquipNotFound)
    kungfu_id = equip_data["data"]["Kungfu"]["KungfuID"]
    current_jcl_line = TuilanData(equip_data).output_jcl_line()
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
    # print(old_instance.jcl_data)
    # print(new_instance.jcl_data)
    new_data = await new_instance.calculate(loop_code)
    if not isinstance(old_data, dict) or not isinstance(new_data, dict):
        await equip_compare.finish(cast(str, old_data))
    msg = f"当前DPS：{old_data['damage_per_second']}\n更新DPS：{new_data['damage_per_second']}"
    await equip_compare.finish(msg)

taixujianyi_calc_matcher = on_command("jx3_calculator_jc", aliases={"剑纯计算器"}, priority=5, force_whitespace=True)

@taixujianyi_calc_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        matcher.stop_propagation()
        return
    raw_arg = args.extract_plain_text().split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await taixujianyi_calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：剑纯计算器 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await taixujianyi_calc_matcher.finish(PROMPT.ServerNotExist)
    instance = await TaixujianyiCalculator.with_name(name, server, "JCPVE")
    if isinstance(instance, str):
        await taixujianyi_calc_matcher.finish(instance)
    income_ver = Preference(event.user_id, "", "").setting("计算器增益")
    income_code = INCOMES[income_ver]
    instance.income_list = income_code
    instance.income_ver = income_ver
    loops = await instance.get_loop()
    if isinstance(loops, str):
        await taixujianyi_calc_matcher.finish(loops)
    state["loops"] = loops
    state["instance"] = instance
    msg = "请选择计算循环！"
    num = 1
    for loop_name in loops:
        msg += f"\n{num}. {loop_name}"
        num += 1
    await taixujianyi_calc_matcher.send(msg)

@taixujianyi_calc_matcher.got("loop_order")
async def _(event: GroupMessageEvent, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await taixujianyi_calc_matcher.finish("循环选择有误，请重新发起命令！")
    loops: dict[str, dict] = state["loops"]
    instance: TaixujianyiCalculator = state["instance"]
    if int(num) > len(list(loops)):
        await taixujianyi_calc_matcher.finish("超出可选范围，请重新发起命令！")
    loop_code: dict[str, str] = loops[list(loops)[int(num)-1]]
    data = await instance.image(loop_code)
    await taixujianyi_calc_matcher.finish(data)

zixiagong_calc_matcher = on_command("jx3_calculator_qc", aliases={"气纯计算器"}, priority=5, force_whitespace=True)

@zixiagong_calc_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        matcher.stop_propagation()
        return
    raw_arg = args.extract_plain_text().split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await zixiagong_calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：气纯计算器 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await zixiagong_calc_matcher.finish(PROMPT.ServerNotExist)
    instance = await ZixiagongCalculator.with_name(name, server, "JCPVE")
    if isinstance(instance, str):
        await zixiagong_calc_matcher.finish(instance)
    income_ver = Preference(event.user_id, "", "").setting("计算器增益")
    formation_ver = Preference(event.user_id, "", "").setting("计算器阵眼")
    income_code = INCOMES[income_ver]
    instance.income_list = income_code
    instance.income_ver = income_ver
    instance.formation_list = FORMATIONS[formation_ver]
    instance.formation_name = formation_ver
    loops = await instance.get_loop()
    if isinstance(loops, str):
        await zixiagong_calc_matcher.finish(loops)
    state["loops"] = loops
    state["instance"] = instance
    msg = "请选择计算循环！"
    num = 1
    for loop_name in loops:
        msg += f"\n{num}. {loop_name}"
        num += 1
    await zixiagong_calc_matcher.send(msg)

@zixiagong_calc_matcher.got("loop_order")
async def _(event: GroupMessageEvent, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await zixiagong_calc_matcher.finish("循环选择有误，请重新发起命令！")
    loops: dict[str, dict] = state["loops"]
    instance: ZixiagongCalculator = state["instance"]
    if int(num) > len(list(loops)):
        await zixiagong_calc_matcher.finish("超出可选范围，请重新发起命令！")
    loop_code: dict[str, str] = loops[list(loops)[int(num)-1]]
    data = await instance.image(loop_code)
    await zixiagong_calc_matcher.finish(data)

def check_jcl_name_jx3bla(filename: str) -> bool:
    if not filename.startswith("IKS-"):
        return False
    pattern = re.compile(
        r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-[\u4e00-\u9fff·\d]+(?:\(\d+\))?-[\u4e00-\u9fff·\d]+(?:\(\d+\))?\.jcl$"
    )
    return bool(pattern.match(filename[4:]))

def check_jcl_name_cqc(filename: str) -> bool:
    if not filename.startswith("CQC-"):
        return False
    pattern = re.compile(
        r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-[\u4e00-\u9fff·\d]+(?:\(\d+\))?-[\u4e00-\u9fff·\d]+(?:\(\d+\))?\.jcl$"
    )
    return bool(pattern.match(filename[4:]))

@notice.handle()
async def _(bot: Bot, event: GroupUploadNoticeEvent):
    if not check_jcl_name_jx3bla(event.file.name):
        return
    else:
        try:
            image = await RDPSCalculator(event.file.name[4:], event.model_dump()["file"]["url"])
        except json.decoder.JSONDecodeError:
            await bot.send_group_msg(group_id=event.group_id, message="啊哦，警长的服务器目前似乎暂时有些小问题，请稍后再使用JCL分析？")
        await bot.send_group_msg(group_id=event.group_id, message=Message(image))

@notice.handle()
async def _(bot: Bot, event: GroupUploadNoticeEvent):
    if not check_jcl_name_cqc(event.file.name):
        return
    else:
        try:
            image = await CQCAnalyze(event.file.name[4:], event.model_dump()["file"]["url"])
        except json.decoder.JSONDecodeError:
            await bot.send_group_msg(group_id=event.group_id, message="啊哦，音卡的服务器目前似乎有些小问题，请稍后再使用JCL分析？")
        await bot.send_group_msg(group_id=event.group_id, message=Message(image))