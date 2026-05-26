from typing import Any, cast, Callable
from nonebot import on_command
from nonebot.params import CommandArg, Arg, RawCommand
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent, GroupUploadNoticeEvent, MessageSegment as ms

from src.config import Config
from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.const.jx3.kungfu import Kungfu
from src.utils.analyze import Locations, check_number
from src.utils.network import Request
from src.utils.database.player import search_player, get_uid_data
from src.utils.database.attributes import JX3PlayerAttribute
from src.utils.permission import check_permission, denied

from src.plugins.notice import notice
from src.plugins.jx3.calculator.compare import EquipInfo, get_equip_list
from src.plugins.preferences.app import Preference
from src.plugins.jx3.equip.equip_config import get_equip_image

from .jx3box import JX3BOXCalculator
from .base import FORMATIONS, INCOMES
from .universe import UniversalCalculator
from .traverse import (
    delete_rating_cache,
    equipment_hash,
    get_rating_cache,
    render_rating_table_image,
    request_equipment_ratings,
    save_rating_cache,
)
from .rdps import BLACalculator, TRDCalculator
from .jcl_analyze import CQCAnalyze, FALAnalyze, YXCAnalyze, RODAnalyze, HPSAnalyze, CALAnalyze, ASNAnalyze, THRAnalyze, THFAnalyze, LGZAnalyze
from . import equipment_rating as equipment_rating_module
import re
import json
import copy
import asyncio

calc_matcher = on_command("jx3_calculator", aliases={"计算器", "T计算器", "QC计算器", "JC计算器", "TL计算器", "JY计算器", "WX计算器"}, priority=5, force_whitespace=True)
calculator_support_matcher = on_command("jx3_calculator_support", aliases={"计算器支持", "计算器心法", "计算器支持心法"}, priority=5, force_whitespace=True)
equipment_rating_matcher = on_command("jx3_equipment_rating", aliases={"装备评级"}, priority=5, force_whitespace=True)
equipment_rating_support_matcher = on_command("jx3_equipment_rating_support", aliases={"装备评级支持", "装备评级心法", "装备评级支持心法"}, priority=5, force_whitespace=True)
rd_analysis_support_matcher = on_command("jx3_rd_analysis_support", aliases={"RD分析支持", "rd分析支持", "Rd分析支持"}, priority=5, force_whitespace=True)

RD_ANALYSIS_SUPPORT_TEXT = (
    "当前 RD 分析支持通过上传群文件触发：\n"
    "【BLA-】单 BOSS 全程 RHPS+RDPS 分析（powered by 剑三警长）\n"
    "【TRD-】唐怀仁 P1 阶段 RDPS 分析（powered by 剑三警长）\n"
    "文件名格式：<前缀>YYYY-MM-DD-HH-MM-SS-<副本名>(副本ID)-<首领名>(首领ID).jcl\n"
    "示例：TRD-2026-05-18-20-52-10-25人英雄阆风悬城(795)-须罗巨傀(137175).jcl\n"
    "使用方式：把符合格式的 .jcl 文件上传到群文件，机器人会自动分析。"
)


def _calculator_support_kungfu_ids() -> list[int]:
    ids: set[int] = set()
    for kungfu_id in Kungfu.kungfu_internel_id.values():
        try:
            ids.add(int(kungfu_id))
        except (TypeError, ValueError):
            continue
    return sorted(ids)


async def _fetch_calculator_loops(kungfu_id: int) -> list[dict[str, Any]]:
    try:
        response = await Request(
            f"{Config.jx3.api.calculator_url}/loops",
            params={"kungfu_id": kungfu_id},
        ).get(timeout=8)
        if response.status_code >= 400:
            return []
        result = response.json()
    except Exception:
        return []
    if result.get("code") != 200:
        return []
    loops = result.get("data") or []
    return loops if isinstance(loops, list) else []


async def _fetch_calculator_supported_kungfus() -> list[dict[str, Any]]:
    kungfu_ids = _calculator_support_kungfu_ids()
    loop_results = await asyncio.gather(
        *(_fetch_calculator_loops(kungfu_id) for kungfu_id in kungfu_ids),
    )
    supported_by_name: dict[str, dict[str, Any]] = {}
    for kungfu_id, loops in zip(kungfu_ids, loop_results):
        if not loops:
            continue
        kungfu = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True)
        if kungfu.name is None:
            continue
        # /loops 会把部分移动端心法映射到旗舰端，这里按最终展示心法去重。
        existing = supported_by_name.get(kungfu.name)
        if existing is None:
            supported_by_name[kungfu.name] = {
                "kungfu_id": kungfu_id,
                "name": kungfu.name,
                "school": kungfu.school or "其他",
                "loops": loops,
                "alias_kungfu_ids": [kungfu_id],
            }
            continue
        existing.setdefault("alias_kungfu_ids", []).append(kungfu_id)
        existing.setdefault("loops", []).extend(loops)
    return sorted(supported_by_name.values(), key=_calculator_support_sort_key)


def _format_calculator_loop(loop: dict[str, Any]) -> str:
    name = str(loop.get("name") or "").strip()
    if not name:
        return "未命名循环"
    weapon, separator, loop_name = name.partition("_")
    if not separator:
        return name
    parts = [part.strip() for part in [weapon, loop_name] if part.strip()]
    return " · ".join(parts) or name


def _calculator_support_sort_key(item: dict[str, Any]) -> int:
    try:
        return int(item.get("kungfu_id") or 0)
    except (TypeError, ValueError):
        return 0


def _find_calculator_supported_kungfu(items: list[dict[str, Any]], kungfu_id: int) -> dict[str, Any] | None:
    for item in items:
        if _calculator_support_sort_key(item) == kungfu_id:
            return item
        if kungfu_id in [int(alias_id) for alias_id in item.get("alias_kungfu_ids") or []]:
            return item
    return None


def _format_calculator_support_list(items: list[dict[str, Any]]) -> str:
    if not items:
        return "当前 calculator 没有可用的计算器心法，或 calculator 服务未连接。"

    school_groups: dict[str, list[dict[str, Any]]] = {}
    for item in sorted(items, key=_calculator_support_sort_key):
        school_groups.setdefault(str(item.get("school") or "其他"), []).append(item)

    lines = [f"当前计算器支持 {len(items)} 个心法："]
    for school, school_items in sorted(
        school_groups.items(),
        key=lambda group: min(_calculator_support_sort_key(item) for item in group[1]),
    ):
        names = "、".join(
            str(item.get("name") or "未知心法")
            for item in sorted(school_items, key=_calculator_support_sort_key)
        )
        lines.append(f"{school}：{names}")
    lines.append("查询单个心法：计算器支持 <心法名>")
    lines.append("计算器使用示例：计算器 剑胆琴心 倦收天")
    return "\n".join(lines)


def _format_calculator_support_detail(item: dict[str, Any]) -> str:
    loop_names: list[str] = []
    for loop in item.get("loops") or []:
        loop_name = _format_calculator_loop(loop)
        if loop_name not in loop_names:
            loop_names.append(loop_name)
    lines = [
        f"计算器支持：{item.get('school') or '其他'}·{item.get('name') or '未知心法'}",
        f"可用循环：{len(loop_names)} 个",
    ]
    for index, loop_name in enumerate(loop_names, start=1):
        lines.append(f"{index}. {loop_name}")
    lines.append("计算器使用示例：计算器 剑胆琴心 倦收天")
    return "\n".join(lines)


@rd_analysis_support_matcher.handle()
async def _():
    await rd_analysis_support_matcher.finish(RD_ANALYSIS_SUPPORT_TEXT)


@calculator_support_matcher.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    query = args.extract_plain_text().strip()
    if len(query.split()) > 1:
        await matcher.finish("参考格式：计算器支持\n参考格式：计算器支持 <心法名>")
    items = await _fetch_calculator_supported_kungfus()
    if query == "":
        await matcher.finish(_format_calculator_support_list(items))
    if not items:
        await matcher.finish("当前 calculator 没有可用的计算器心法，或 calculator 服务未连接。")
    if query.isdigit():
        kungfu_id = int(query)
    else:
        kungfu_id = Kungfu(query).id or 0
    if kungfu_id == 0:
        await matcher.finish(PROMPT.KungfuNotExist)
    item = _find_calculator_supported_kungfu(items, kungfu_id)
    if item is None:
        kungfu = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True)
        await matcher.finish(f"当前计算器暂不支持 {kungfu.name or '该心法'}。")
    await matcher.finish(_format_calculator_support_detail(item))


@equipment_rating_support_matcher.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    await equipment_rating_module.handle_equipment_rating_support(matcher, args)


@equipment_rating_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg()):
    await equipment_rating_module.handle_equipment_rating(event, matcher, state, args)


@equipment_rating_matcher.got("rating_jcl_order")
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, rating_jcl_order: Message = Arg()):
    await equipment_rating_module.handle_equipment_rating_loop_order(event, matcher, state, rating_jcl_order)

@calc_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg(), cmd: str = RawCommand()):
    if args.extract_plain_text() == "":
        matcher.stop_propagation()
        return
    raw_arg = args.extract_plain_text().split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：计算器 <服务器> <角色名>\n计算器 <魔盒配装ID>")
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
    if "WX" in cmd:
        tag = "WXPVE"
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
    is_custom = Preference(event.user_id, "", "").setting("计算器来源") == "自定义"
    income_code = INCOMES[income_ver]
    instance.income_list = income_code
    instance.income_ver = income_ver
    instance.formation_list = FORMATIONS[formation_ver]
    instance.formation_name = formation_ver

    loops = await instance.get_loop(event.user_id if is_custom else 0)
    if isinstance(loops, str):
        unsupported_msg = "该玩家下线时的心法当前尚未实现计算器，可尝试使用指定计算器（如有）或等待该心法支持！\n也可能是当前使用的计算器循环库中并无该心法，请切换公用循环库或自定义循环库，详情见「偏好」。"
        if is_custom:
            unsupported_msg = "未找到已上传的该心法 JCL，请切换至公用循环库或自行上传该心法循环！\n切换方式：发送「偏好 计算器来源 公用」"
        await calc_matcher.finish(unsupported_msg)
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

    is_custom = Preference(event.user_id, "", "").setting("计算器来源") == "自定义"
    data = await instance.image(loop_code, event.user_id if is_custom else 0)

    if state["pzid"] != 0:
        equip_image = ms.image(await get_equip_image(str(state["pzid"])))
        await calc_matcher.send(equip_image)
    await calc_matcher.finish(data)

equip_compare = on_command("jx3_equip_compare", aliases={"装备对比", "T装备对比", "QC装备对比", "JC装备对比", "TL装备对比", "JY装备对比", "WX装备对比"}, priority=5, force_whitespace=True)

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
    if "WX" in cmd:
        tag = "WXPVE"
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

    equip_name = equip
    equips = await get_equip_list(equip_name)
    if not equips:
        await equip_compare.finish(f"未找到装备「{equip_name}」，请检查装备名，或尝试输入更完整的装备名称。")
    msg = "请从下面选择装备进行对比！"
    num = 1
    for equip_info in equips:
        msg += f"\n{num}. ({equip_info.subkind}) {equip_info.name}\n{equip_info.quality} {' '.join(equip_info.attr)}"
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
    index = int(num)
    if index < 1 or index > len(equips):
        await equip_compare.finish("超出可选范围，请重新发起命令！")
    equip = equips[index - 1]
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

    is_custom = Preference(event.user_id, "", "").setting("计算器来源") == "自定义"
    loops = await new_dps_data.get_loop(event.user_id if is_custom else 0)
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

    is_custom = Preference(event.user_id, "", "").setting("计算器来源") == "自定义"

    old_data = await old_instance.calculate(loop_code, event.user_id if is_custom else 0)
    new_data = await new_instance.calculate(loop_code, event.user_id if is_custom else 0)
    if not isinstance(old_data, dict) or not isinstance(new_data, dict):
        await equip_compare.finish(cast(str, old_data))
    old_dps = old_data['damage_per_second']
    new_dps = new_data['damage_per_second']
    margin = str(round((new_dps / old_dps - 1) * 100, 3)) + "%"
    msg = f"当前DPS：{old_dps}\n更新DPS：{new_dps}\n提升幅度：{margin}"
    if is_custom:
        msg += "\n提示：当前正在使用自定义循环！"
    await equip_compare.finish(msg)

remove_calculator_loop_matcher = on_command("jx3_rm_calc_loop", aliases={"删除循环"}, priority=5, force_whitespace=True)

@remove_calculator_loop_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    kungfu = args.extract_plain_text()
    params = {"user_id": event.user_id}
    if kungfu == "all":
        params["all_delete"] = True
    else:
        kungfu_id = Kungfu(kungfu).id
        if kungfu_id is None:
            await remove_calculator_loop_matcher.finish("心法输入有误，请检查后重试！")
        params["kungfu_id"] = kungfu_id
    result = (await Request(f"{Config.jx3.api.calculator_url}/delete_loop", params=params).get()).json()
    if result["code"] == 200:
        await remove_calculator_loop_matcher.finish("循环删除成功！")
    else:
        await remove_calculator_loop_matcher.finish("循环删除失败！" + result["msg"])

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
    if check_jcl_name(event.file.name, "BLA-"):
        analyzer = BLACalculator
    elif check_jcl_name(event.file.name, "TRD-"):
        analyzer = TRDCalculator
    elif check_jcl_name(event.file.name, "CQC-"):
        analyzer = CQCAnalyze
    elif check_jcl_name(event.file.name, "FAL-"):
        analyzer = FALAnalyze
    elif check_jcl_name(event.file.name, "YXC-"):
        analyzer = YXCAnalyze
    elif check_jcl_name(event.file.name, "ROD-"):
        analyzer = RODAnalyze
    # elif check_jcl_name(event.file.name, "HPS-"):
    #     analyzer = HPSAnalyze
    elif event.file.name.startswith("CAL-"):
        analyzer = CALAnalyze
    elif check_jcl_name(event.file.name, "ASN-"):
        analyzer = ASNAnalyze
    elif check_jcl_name(event.file.name, "THR-"):
        analyzer = THRAnalyze
    elif check_jcl_name(event.file.name, "THF-"):
        analyzer = THFAnalyze
    elif check_jcl_name(event.file.name, "LGZ-"):
        analyzer = LGZAnalyze 
    else:
        return
    
    if analyzer is not None:
        anonymous_preference = Preference(event.user_id, "", "").setting("匿名分析")
        is_anonymous = anonymous_preference == "开启"
        try:
            url = event.model_dump()["file"]["url"]
        except KeyError:
            file_id = event.model_dump()["file"]["id"]
            bus_id = event.model_dump()["file"]["busid"]
            file_data = await bot.call_api("get_group_file_url", group_id=event.group_id, file_id=file_id, bus_id=bus_id)
            url = file_data["url"]
        try:
            image = await analyzer(event.file.name[4:], url, is_anonymous, event.user_id)
            await bot.send_group_msg(group_id=event.group_id, message=Message(image))
        except json.decoder.JSONDecodeError:
            await bot.send_group_msg(group_id=event.group_id, message="啊哦，音卡的服务器目前似乎暂时有些小问题，请稍后再使用JCL分析？")
