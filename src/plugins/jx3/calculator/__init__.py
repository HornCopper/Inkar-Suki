from nonebot import on_command
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent, GroupUploadNoticeEvent

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.analyze import check_number
from src.plugins.notice import notice

from .lxg import LingxueCalculator
from .wf import WufangCalculator
from .bxj import BingxinjueCalculator
from .txjy import TaixujianyiCalculator
from .tll import TielaolvCalculator
from .mzllt import MingzunliulitiCalculator
from .tgy import TieguyiCalculator
from .xsj import XisuijingCalculator
from .lhj import LinghaijueCalculator
from .rdps import RDPSCalculator

import re
import json

yinlongjue_calc_matcher = on_command("jx3_calculator_lyj", aliases={"凌雪计算器"}, priority=5, force_whitespace=True)

@yinlongjue_calc_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
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

wufang_calc_matcher = on_command("jx3_calculator_wf", aliases={"无方计算器"}, priority=5, force_whitespace=True)

@wufang_calc_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    raw_arg = args.extract_plain_text().split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await wufang_calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：无方计算器 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await wufang_calc_matcher.finish(PROMPT.ServerNotExist)
    instance = await WufangCalculator.with_name(name, server, "DPSPVE")
    if isinstance(instance, str):
        await wufang_calc_matcher.finish(instance)
    loops = await instance.get_loop()
    state["loops"] = loops
    state["instance"] = instance
    msg = "请选择计算循环！"
    num = 1
    for loop_name in loops:
        msg += f"\n{num}. {loop_name}"
        num += 1
    await wufang_calc_matcher.send(msg)

@wufang_calc_matcher.got("loop_order")
async def _(event: GroupMessageEvent, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await wufang_calc_matcher.finish("循环选择有误，请重新发起命令！")
    loops: dict[str, dict] = state["loops"]
    instance: WufangCalculator = state["instance"]
    if int(num) > len(list(loops)):
        await wufang_calc_matcher.finish("超出可选范围，请重新发起命令！")
    loop_code: dict[str, str] = loops[list(loops)[int(num)-1]]
    data = await instance.image(loop_code)
    await wufang_calc_matcher.finish(data)

bingxinjue_calc_matcher = on_command("jx3_calculator_bx", aliases={"冰心计算器"}, priority=5, force_whitespace=True)

@bingxinjue_calc_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    raw_arg = args.extract_plain_text().split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await bingxinjue_calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：冰心计算器 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await bingxinjue_calc_matcher.finish(PROMPT.ServerNotExist)
    instance = await BingxinjueCalculator.with_name(name, server, "DPSPVE")
    if isinstance(instance, str):
        await bingxinjue_calc_matcher.finish(instance)
    loops = await instance.get_loop()
    state["loops"] = loops
    state["instance"] = instance
    msg = "请选择计算循环！"
    num = 1
    for loop_name in loops:
        msg += f"\n{num}. {loop_name}"
        num += 1
    await bingxinjue_calc_matcher.send(msg)

@bingxinjue_calc_matcher.got("loop_order")
async def _(event: GroupMessageEvent, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await bingxinjue_calc_matcher.finish("循环选择有误，请重新发起命令！")
    loops: dict[str, dict] = state["loops"]
    instance: BingxinjueCalculator = state["instance"]
    if int(num) > len(list(loops)):
        await bingxinjue_calc_matcher.finish("超出可选范围，请重新发起命令！")
    loop_code: dict[str, str] = loops[list(loops)[int(num)-1]]
    data = await instance.image(loop_code)
    await bingxinjue_calc_matcher.finish(data)

taixujianyi_calc_matcher = on_command("jx3_calculator_jc", aliases={"剑纯计算器"}, priority=5, force_whitespace=True)

@taixujianyi_calc_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
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
    loops = await instance.get_loop()
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

tielaolv_calc_matcher = on_command("jx3_calculator_ct", aliases={"铁牢计算器"}, priority=5, force_whitespace=True)

@tielaolv_calc_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    raw_arg = args.extract_plain_text().split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await tielaolv_calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：铁牢计算器 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await tielaolv_calc_matcher.finish(PROMPT.ServerNotExist)
    instance = await TielaolvCalculator.with_name(name, server, "TPVE")
    if isinstance(instance, str):
        await tielaolv_calc_matcher.finish(instance)
    loops = await instance.get_loop()
    state["loops"] = loops
    state["instance"] = instance
    msg = "请选择计算循环！"
    num = 1
    for loop_name in loops:
        msg += f"\n{num}. {loop_name}"
        num += 1
    await tielaolv_calc_matcher.send(msg)

@tielaolv_calc_matcher.got("loop_order")
async def _(event: GroupMessageEvent, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await tielaolv_calc_matcher.finish("循环选择有误，请重新发起命令！")
    loops: dict[str, dict] = state["loops"]
    instance: TielaolvCalculator = state["instance"]
    if int(num) > len(list(loops)):
        await tielaolv_calc_matcher.finish("超出可选范围，请重新发起命令！")
    loop_code: dict[str, str] = loops[list(loops)[int(num)-1]]
    data = await instance.image(loop_code)
    await tielaolv_calc_matcher.finish(data)

mingzunliuliti_calc_matcher = on_command("jx3_calculator_mt", aliases={"明尊计算器"}, priority=5, force_whitespace=True)

@mingzunliuliti_calc_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    raw_arg = args.extract_plain_text().split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await mingzunliuliti_calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：明尊计算器 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await mingzunliuliti_calc_matcher.finish(PROMPT.ServerNotExist)
    instance = await MingzunliulitiCalculator.with_name(name, server, "TPVE")
    if isinstance(instance, str):
        await mingzunliuliti_calc_matcher.finish(instance)
    loops = await instance.get_loop()
    state["loops"] = loops
    state["instance"] = instance
    msg = "请选择计算循环！"
    num = 1
    for loop_name in loops:
        msg += f"\n{num}. {loop_name}"
        num += 1
    await mingzunliuliti_calc_matcher.send(msg)

@mingzunliuliti_calc_matcher.got("loop_order")
async def _(event: GroupMessageEvent, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await mingzunliuliti_calc_matcher.finish("循环选择有误，请重新发起命令！")
    loops: dict[str, dict] = state["loops"]
    instance: MingzunliulitiCalculator = state["instance"]
    if int(num) > len(list(loops)):
        await mingzunliuliti_calc_matcher.finish("超出可选范围，请重新发起命令！")
    loop_code: dict[str, str] = loops[list(loops)[int(num)-1]]
    data = await instance.image(loop_code)
    await mingzunliuliti_calc_matcher.finish(data)

tieguyi_calc_matcher = on_command("jx3_calculator_tg", aliases={"铁骨计算器"}, priority=5, force_whitespace=True)

@tieguyi_calc_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    raw_arg = args.extract_plain_text().split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await tieguyi_calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：铁骨计算器 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await tieguyi_calc_matcher.finish(PROMPT.ServerNotExist)
    instance = await TieguyiCalculator.with_name(name, server, "TPVE")
    if isinstance(instance, str):
        await tieguyi_calc_matcher.finish(instance)
    loops = await instance.get_loop()
    state["loops"] = loops
    state["instance"] = instance
    msg = "请选择计算循环！"
    num = 1
    for loop_name in loops:
        msg += f"\n{num}. {loop_name}"
        num += 1
    await tieguyi_calc_matcher.send(msg)

@tieguyi_calc_matcher.got("loop_order")
async def _(event: GroupMessageEvent, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await tieguyi_calc_matcher.finish("循环选择有误，请重新发起命令！")
    loops: dict[str, dict] = state["loops"]
    instance: TieguyiCalculator = state["instance"]
    if int(num) > len(list(loops)):
        await tieguyi_calc_matcher.finish("超出可选范围，请重新发起命令！")
    loop_code: dict[str, str] = loops[list(loops)[int(num)-1]]
    data = await instance.image(loop_code)
    await tieguyi_calc_matcher.finish(data)

xisuijing_calc_matcher = on_command("jx3_calculator_hst", aliases={"洗髓计算器"}, priority=5, force_whitespace=True)

@xisuijing_calc_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    raw_arg = args.extract_plain_text().split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await xisuijing_calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：洗髓计算器 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await xisuijing_calc_matcher.finish(PROMPT.ServerNotExist)
    instance = await XisuijingCalculator.with_name(name, server, "TPVE")
    if isinstance(instance, str):
        await xisuijing_calc_matcher.finish(instance)
    loops = await instance.get_loop()
    state["loops"] = loops
    state["instance"] = instance
    msg = "请选择计算循环！"
    num = 1
    for loop_name in loops:
        msg += f"\n{num}. {loop_name}"
        num += 1
    await xisuijing_calc_matcher.send(msg)

@xisuijing_calc_matcher.got("loop_order")
async def _(event: GroupMessageEvent, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await xisuijing_calc_matcher.finish("循环选择有误，请重新发起命令！")
    loops: dict[str, dict] = state["loops"]
    instance: XisuijingCalculator = state["instance"]
    if int(num) > len(list(loops)):
        await xisuijing_calc_matcher.finish("超出可选范围，请重新发起命令！")
    loop_code: dict[str, str] = loops[list(loops)[int(num)-1]]
    data = await instance.image(loop_code)
    await xisuijing_calc_matcher.finish(data)

linghaijue_calc_matcher = on_command("jx3_calculator_lhj", aliases={"蓬莱计算器"}, priority=5, force_whitespace=True)

@linghaijue_calc_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    raw_arg = args.extract_plain_text().split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await linghaijue_calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：蓬莱计算器 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await linghaijue_calc_matcher.finish(PROMPT.ServerNotExist)
    instance = await LinghaijueCalculator.with_name(name, server, "DPSPVE")
    if isinstance(instance, str):
        await linghaijue_calc_matcher.finish(instance)
    loops = await instance.get_loop()
    state["loops"] = loops
    state["instance"] = instance
    msg = "请选择计算循环！"
    num = 1
    for loop_name in loops:
        msg += f"\n{num}. {loop_name}"
        num += 1
    await linghaijue_calc_matcher.send(msg)

@linghaijue_calc_matcher.got("loop_order")
async def _(event: GroupMessageEvent, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await linghaijue_calc_matcher.finish("循环选择有误，请重新发起命令！")
    loops: dict[str, dict] = state["loops"]
    instance: LinghaijueCalculator = state["instance"]
    if int(num) > len(list(loops)):
        await linghaijue_calc_matcher.finish("超出可选范围，请重新发起命令！")
    loop_code: dict[str, str] = loops[list(loops)[int(num)-1]]
    data = await instance.image(loop_code)
    await linghaijue_calc_matcher.finish(data)

def check_jcl_name(filename: str) -> bool:
    if not filename.startswith("IKS-"):
        return False
    pattern = re.compile(
        r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-[\u4e00-\u9fff·\d]+(?:\(\d+\))?-[\u4e00-\u9fff·\d]+(?:\(\d+\))?\.jcl$"
    )
    return bool(pattern.match(filename[4:]))

@notice.handle()
async def _(bot: Bot, event: GroupUploadNoticeEvent):
    if not check_jcl_name(event.file.name):
        return
    else:
        try:
            image = await RDPSCalculator(event.file.name[4:], event.model_dump()["file"]["url"])
        except json.decoder.JSONDecodeError:
            await bot.send_group_msg(group_id=event.group_id, message="啊哦，警长的服务器目前似乎暂时有些小问题，请稍后再使用JCL分析？")
        await bot.send_group_msg(group_id=event.group_id, message=Message(image))