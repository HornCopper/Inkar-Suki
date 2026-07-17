from pathlib import Path
from typing import Any, cast, Callable
from jinja2 import Template
from nonebot import on_command
from nonebot.log import logger
from nonebot.params import CommandArg, Arg, RawCommand
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent, GroupUploadNoticeEvent, MessageSegment as ms

from src.config import Config
from src.const.path import ASSETS, DATA, build_path
from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.const.jx3.kungfu import Kungfu
from src.utils.analyze import Locations, check_number
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.file import read, write
from src.utils.database.player import search_player
from src.utils.database.attributes import JX3PlayerAttribute
from src.utils.permission import check_permission, denied

from src.plugins.notice import notice
from src.plugins.jx3.calculator.compare import EquipInfo, get_equip_list
from src.plugins.preferences.app import Preference
from src.plugins.jx3.equip.equip_config import get_equip_image

from .jx3box import JX3BOXCalculator
from .base import FORMATIONS, FULL_INCOME_WITH_CONSUMABLES, get_calculator_income_codes, normalize_calculator_jcl_data
from .universe import UniversalCalculator
from .loop_selection import (
    calculator_loop_entries as _calculator_loop_entries,
    format_calculator_loop_selection as _format_calculator_loop_selection,
)
from .timeline_render import (
    _buff_overlays_svg,
    _chart_svg,
    _format_compact_number,
    _format_seconds,
)
from .traverse import (
    delete_rating_cache,
    equipment_hash,
    get_rating_cache,
    render_rating_table_image,
    request_equipment_ratings,
    save_rating_cache,
)
from .rdps import BLACalculator, TRDCalculator
from .jcl_analyze import CQCAnalyze, FALAnalyze, YXCAnalyze, RODAnalyze, DPSAnalyze, CALAnalyze, ASNAnalyze, THRAnalyze, THFAnalyze, LGZAnalyze, LNXAnalyze
from ._template import calculator_timeline_template, custom_loop_help_template

from .therapy_panel import therapy_panel
from . import equipment_rating as equipment_rating_module
import re
import json
import copy
import asyncio
import html
import math
import random


def _prefixed_command_aliases(base_command: str, prefixes: tuple[str, ...]) -> set[str]:
    aliases = {base_command}
    for prefix in prefixes:
        variants = {""}
        for char in prefix:
            variants = {variant + letter for variant in variants for letter in {char.lower(), char.upper()}}
        aliases.update(f"{variant}{base_command}" for variant in variants)
    return aliases


CALCULATOR_PREFIXES = ("T", "QC", "JC", "TL", "JY", "WX")
SPECIAL_PVE_KUNGFU_TAGS = {
    10014: "QCPVE",
    10015: "JCPVE",
    10224: "JYPVE",
    10225: "TLPVE",
    10821: "WXPVE",
}

DEFAULT_DAMAGE_TIMELINE_BIN_SIZE = 2.5
DEFAULT_DAMAGE_TIMELINE_ROLLING_WINDOW = 10
DEFAULT_DAMAGE_TIMELINE_KLINE_TARGET_CANDLES = 110
DEFAULT_DAMAGE_TIMELINE_KLINE_MA_PERIODS = (5, 10, 20)
KLINE_GAME_INITIAL_CASH = 1000000
KLINE_GAME_PREMIUM_RATE = 0.03
KLINE_GAME_OPTION_TERMS = (15, 30, 45, 60)
KLINE_GAME_MIN_REMAINING = 30
KLINE_GAME_MIN_HISTORY = 30
KLINE_GAME_HISTORY_WINDOW = 120
PUBLIC_LOOP_DEFAULT_APPROVAL_GROUP_ID = 1018743771
PUBLIC_LOOP_APPROVAL_CONFIG_PATH = build_path(DATA, ["jx3", "public_loop_approval.json"])
PUBLIC_LOOP_APPROVE_PERMISSION_NODE = "jx3.calculator.public_loop.approve"
PUBLIC_LOOP_CONFIG_PERMISSION_NODE = "jx3.calculator.public_loop.config"
CALCULATOR_LOOP_RENAME_OTHER_PERMISSION_NODE = "jx3.calculator.loop.rename_other"

RD_ANALYSIS_SUPPORT_TEXT = (
    "当前 RD 分析支持通过上传群文件触发：\n"
    "【BLA-】单 BOSS 全程 RHPS+RDPS 分析（powered by 剑三警长）\n"
    "【TRD-】唐怀仁 P1 阶段 RDPS 分析（powered by 剑三警长）\n"
    "文件名格式：<前缀>YYYY-MM-DD-HH-MM-SS-<副本名>(副本ID)-<首领名>(首领ID).jcl\n"
    "示例：TRD-2026-05-18-20-52-10-25人英雄阆风悬城(795)-须罗巨傀(137175).jcl\n"
    "使用方式：把符合格式的 .jcl 文件上传到群文件，机器人会自动分析。"
)

JCL_ANALYSIS_HELP_TEXT = (
    "【Inkar Suki JCL分析简短说明】\n"
    "音卡可以通过JCL分析副本战斗时各种情况，需在打之前勾选茗伊战斗事件记录（见图片），不同的前缀有不同的效果，前缀直接在文件名前方加上后直接上传至有音卡的群（如果群主不嫌消息多的话）\n\n"
    "【BLA-】 单BOSS 全程 RHPS+RDPS分析（powered by 剑三警长）\n"
    "【LNX-】鲁念雪 每阶段减伤/治疗/化解贡献统计\n"
    "【ASN-】阿史那承庆 QTE计数+死侍HPS统计\n"
    "【THR-】唐怀仁P1 DPS统计+榜单\n"
    "【TRD-】唐怀仁 P1 阶段 RDPS 分析（powered by 剑三警长）\n"
    "裁剪区间：开始战斗-BOSS喊话\n"
    "【THF-】唐怀仁P3 DPS统计\n"
    "裁剪区间：毁灭读条-叶鸦出现\n"
    "【LGZ-】柳公子传功记录\n"
    "【FAL-】前三次攻击记录，用于查开怪，尤其是阿里曼幻身的圣柱\n"
    "【YXC-】尹雪尘承伤统计，注意只会记录每个玩家的有效而非全部治疗\n"
    "【ROD-】重伤记录统计\n"
    "注意，复制同目录的文件会有“ - 副本”后缀，需要删掉。"
)
JCL_ANALYSIS_HELP_IMAGE_PATH = build_path(
    ASSETS,
    ["image", "jx3", "calculator", "jcl_analysis_mingyi_record.jpg"],
)


def _jcl_analysis_help_message():
    image_path = Path(JCL_ANALYSIS_HELP_IMAGE_PATH)
    if not image_path.exists():
        return JCL_ANALYSIS_HELP_TEXT
    return JCL_ANALYSIS_HELP_TEXT + "\n" + ms.image(Request(image_path.as_uri()).local_content)

CALCULATOR_HELP_TEXT = (
    "计算器简短说明：\n"
    "音卡无法通过世界发言自动更新装备，需手动提交属性。\n"
    "操作路径：茗伊插件 → 角色统计 → 装备统计 → 右上角导出装备码。\n\n"
    "提交装备\n"
    "格式：<提交属性 区服 角色名 心法名称>\n"
    "然后粘贴导出的装备码即可完成提交。\n\n"
    "计算器唤醒指令\n"
    "T心法及双心法（如气纯、剑纯等）需要添加对应前缀，所有后缀均不写心法名称。\n"
    "指令格式：\n"
    "<T计算器 区服 角色名>\n"
    "<QC/JY/TL计算器 区服 角色名>\n\n"
    "其余心法无需加前缀和心法名称，直接使用：\n"
    "<计算器 区服 角色名>\n\n"
    "装备评级\n"
    "格式：<装备评级 区服 角色名 [心法名称] [评级列表]>\n"
    "或：<装备评级 魔盒配装ID [评级列表]>\n\n"
    "计算器的 JCL 由玩家提供，不能代表职业整体水平，且使用他人循环所产生的不认可，可以自行提供 JCL 进行计算，如何打造自身专属循环详情请看文档。\n"
    "计算器详细说明书请看：https://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/calculator"
)


def _calculator_help_message():
    image_path = Path(
        build_path(ASSETS, ["image", "jx3", "calculator", "calculator_equipment_export.jpg"])
    )
    if not image_path.exists():
        return CALCULATOR_HELP_TEXT
    return CALCULATOR_HELP_TEXT + "\n" + ms.image(Request(image_path.as_uri()).local_content)


async def _render_custom_loop_help_image():
    jcl_export_image = Path(
        build_path(ASSETS, ["image", "jx3", "calculator", "custom_loop_jcl_export.png"])
    ).as_uri()
    html_source = custom_loop_help_template.replace("__JCL_EXPORT_IMAGE__", html.escape(jcl_export_image, quote=True))
    return await generate(
        html_source,
        ".guide",
        False,
        segment=True,
        viewport={"width": 980, "height": 2400},
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


def _calculator_tag_from_command(cmd: str) -> str:
    normalized_cmd = cmd.upper()
    tag = "TPVE" if normalized_cmd and normalized_cmd[0] == "T" else "DPSPVE"
    if "QC" in normalized_cmd:
        tag = "QCPVE"
    if "JC" in normalized_cmd:
        tag = "JCPVE"
    if "TL" in normalized_cmd:
        tag = "TLPVE"
    if "JY" in normalized_cmd:
        tag = "JYPVE"
    if "WX" in normalized_cmd:
        tag = "WXPVE"
    return tag


def _calculator_command_has_specific_prefix(cmd: str) -> bool:
    normalized_cmd = cmd.upper()
    return any(normalized_cmd.startswith(prefix) for prefix in CALCULATOR_PREFIXES)


def _calculator_auto_select_pve_tag(kungfu_id: int) -> str | None:
    if kungfu_id in SPECIAL_PVE_KUNGFU_TAGS:
        return SPECIAL_PVE_KUNGFU_TAGS[kungfu_id]
    abbr = Kungfu.with_internel_id(kungfu_id).abbr
    if abbr == "T":
        return "TPVE"
    if abbr == "D":
        return "DPSPVE"
    return None


async def _calculator_pve_tag_options(global_role_id: int) -> list[dict[str, Any]]:
    all_equips = await JX3PlayerAttribute.from_database(global_role_id, "", True)
    if not all_equips:
        return []

    latest_by_kungfu: dict[int, JX3PlayerAttribute] = {}
    for equip in all_equips:
        kungfu_id = int(equip.kungfu_id)
        if equip.tag != "PVE":
            continue
        tag = _calculator_auto_select_pve_tag(kungfu_id)
        if tag is None:
            continue
        current = latest_by_kungfu.get(kungfu_id)
        if current is None or equip.timestamp > current.timestamp:
            latest_by_kungfu[kungfu_id] = equip

    options: list[dict[str, Any]] = []
    for kungfu_id, equip in sorted(latest_by_kungfu.items(), key=lambda item: item[1].timestamp, reverse=True):
        kungfu = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True)
        tag = _calculator_auto_select_pve_tag(kungfu_id)
        if tag is None:
            continue
        options.append(
            {
                "tag": tag,
                "kungfu_id": kungfu_id,
                "name": kungfu.name or str(kungfu_id),
            }
        )
    return options


def _format_special_pve_kungfu_selection(options: list[dict[str, Any]]) -> str:
    msg = "检测到该玩家有多个可用于计算的 PVE 心法装备，请先选择心法："
    for index, option in enumerate(options, start=1):
        msg += f"\n{index}. {option['name']}"
    return msg


async def _resolve_bare_calculator_tag_for_global_role_id(
    global_role_id: int,
    state: T_State,
    *,
    selection_key: str,
) -> str:
    options = await _calculator_pve_tag_options(global_role_id)
    if len(options) == 1:
        return str(options[0]["tag"])
    if len(options) > 1:
        state[selection_key] = options
        return ""
    return "DPSPVE"


def _parse_timeline_command_args(raw_text: str) -> tuple[list[str], float | str]:
    pattern = re.compile(r"(?i)(?:^|\s)bin\s*[=＝]\s*(\S+)(?=\s|$)")
    matches = list(pattern.finditer(raw_text))
    if len(matches) > 1:
        return [], "bin 参数只能填写一次，请重新发起命令！"
    bin_size = DEFAULT_DAMAGE_TIMELINE_BIN_SIZE
    cleaned_text = raw_text
    if matches:
        try:
            bin_size = float(matches[0].group(1))
        except ValueError:
            return [], "bin 参数格式有误，请使用类似 bin=2.5 的格式！"
        if not (1 <= bin_size <= 60):
            return [], "bin 参数范围为 1 到 60 秒，请重新发起命令！"
        cleaned_text = pattern.sub(" ", raw_text, count=1)
    arg = [item for item in cleaned_text.split() if item != "-A"]
    return arg, bin_size


TIMELINE_ARGUMENT_PROMPT = (
    PROMPT.ArgumentCountInvalid
    + "\n参考格式：循环曲线 <服务器> <角色名> bin=2.5"
    + "\n参考格式：循环曲线 <魔盒配装ID> bin=2.5"
    + "\n参考格式：循环对比 <服务器> <角色名> bin=2.5"
    + "\n参考格式：循环对比 <魔盒配装ID> bin=2.5"
    + "\n参考格式：循环k线 <服务器> <角色名> bin=2.5"
    + "\n参考格式：循环k线 <魔盒配装ID> bin=2.5"
)

TIMELINE_HELP_TEXT = (
    "循环曲线参数：\n"
    "1. 角色：<服务器> <角色名>，例如 剑胆琴心 倦收天\n"
    "2. 魔盒配装：<配装ID>\n"
    "3. 可选参数：bin=<秒数>，只影响上图每 N 秒伤害量；默认 bin=2.5，范围 1 到 60\n"
    "4. 累计实时 DPS 固定逐秒计算，不受 bin 参数影响\n"
    "5. 机器人返回循环列表后，选择 1 个循环\n"
    "示例：\n"
    "循环曲线 剑胆琴心 倦收天 bin=2.5\n"
    "循环列表返回后发送：1"
)

TIMELINE_KLINE_HELP_TEXT = (
    "循环K线参数：\n"
    "1. 角色：<服务器> <角色名>，例如 剑胆琴心 倦收天\n"
    "2. 魔盒配装：<配装ID>\n"
    "3. 可选参数：bin=<秒数>，为保持与循环曲线一致可填写；K线按默认 10 秒滚动 DPS 逐秒计算，不受 bin 参数影响\n"
    "4. 机器人返回循环列表后，选择 1 个循环\n"
    "示例：\n"
    "循环k线 剑胆琴心 倦收天 bin=2.5\n"
    "循环列表返回后发送：1"
)

TIMELINE_COMPARE_HELP_TEXT = (
    "循环对比参数：\n"
    "1. 角色：<服务器> <角色名>，例如 剑胆琴心 倦收天\n"
    "2. 魔盒配装：<配装ID>\n"
    "3. 可选参数：bin=<秒数>，只影响上图每 N 秒伤害量；默认 bin=2.5，范围 1 到 60\n"
    "4. 累计实时 DPS 固定逐秒计算，不受 bin 参数影响\n"
    "5. 机器人返回循环列表后，选择 2 个及以上循环，支持空格、半角逗号、全角逗号\n"
    "示例：\n"
    "循环对比 剑胆琴心 倦收天 bin=2.5\n"
    "循环列表返回后发送：1,2 或 1，2，3"
)


async def _resolve_timeline_instance(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    arg: list[str],
    cmd: str,
) -> UniversalCalculator | JX3BOXCalculator | None:
    if len(arg) not in [1, 2]:
        await matcher.finish(TIMELINE_ARGUMENT_PROMPT)
    if len(arg) == 1:
        server = None
        name = arg[0]
    else:
        server = arg[0]
        name = arg[1]

    state["timeline_pzid"] = 0
    tag = _calculator_tag_from_command(cmd)
    is_specific_calculator = _calculator_command_has_specific_prefix(cmd)
    if check_number(name):
        instance = await JX3BOXCalculator.with_pzid(int(name))
        if isinstance(instance, str):
            await matcher.finish(instance)
        state["timeline_pzid"] = int(name)
        return instance
    if name.startswith("g"):
        global_role_id = name[1:]
        if not check_number(global_role_id):
            await matcher.finish("全局玩家ID输入有误，请检查后重试！")
        if not is_specific_calculator:
            resolved_tag = await _resolve_bare_calculator_tag_for_global_role_id(
                int(global_role_id),
                state,
                selection_key="timeline_kungfu_options",
            )
            if resolved_tag == "":
                state["timeline_kungfu_context"] = {
                    "mode": "global",
                    "global_role_id": int(global_role_id),
                }
                await matcher.send(_format_special_pve_kungfu_selection(state["timeline_kungfu_options"]))
                return None
            tag = resolved_tag
        instance = await UniversalCalculator.with_global_role_id(int(global_role_id), tag)
        if isinstance(instance, str):
            await matcher.finish(instance)
        return instance

    server = Server(server, event.group_id).server
    if server is None:
        await matcher.finish(PROMPT.ServerNotExist)
    if not is_specific_calculator:
        player_data = await search_player(role_name=name, server_name=server)
        if player_data.roleId == "":
            await matcher.finish(PROMPT.PlayerNotExist)
        await JX3PlayerAttribute.from_tuilan(player_data.roleId, player_data.serverName, player_data.globalRoleId)
        resolved_tag = await _resolve_bare_calculator_tag_for_global_role_id(
            int(player_data.globalRoleId),
            state,
            selection_key="timeline_kungfu_options",
        )
        if resolved_tag == "":
            state["timeline_kungfu_context"] = {
                "mode": "name",
                "server": server,
                "name": name,
            }
            await matcher.send(_format_special_pve_kungfu_selection(state["timeline_kungfu_options"]))
            return None
        tag = resolved_tag
    instance = await UniversalCalculator.with_name(name, server, tag)
    if isinstance(instance, str):
        await matcher.finish(instance)
    return instance


async def _prepare_timeline_loop_selection(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    instance: UniversalCalculator | JX3BOXCalculator,
    *,
    compare: bool,
    kline: bool,
    bin_size: float,
) -> None:
    is_custom = _apply_calculator_preferences(event, instance)
    loop_entries = await _calculator_loop_entries(instance, event.user_id, is_custom)
    if isinstance(loop_entries, str):
        await matcher.finish(loop_entries)
    state["timeline_loops"] = loop_entries
    state["timeline_instance"] = instance
    state["timeline_is_custom"] = is_custom
    state["timeline_compare"] = compare
    state["timeline_kline"] = kline
    state["timeline_bin_size"] = bin_size
    await matcher.send(_format_timeline_loop_selection(loop_entries, compare=compare, kline=kline))


def _apply_calculator_preferences(event: GroupMessageEvent, instance: UniversalCalculator | JX3BOXCalculator) -> bool:
    income_ver = Preference(event.user_id, "", "").setting("计算器增益")
    formation_ver = Preference(event.user_id, "", "").setting("计算器阵眼")
    is_custom = Preference(event.user_id, "", "").setting("计算器来源") == "自定义"
    income_code = get_calculator_income_codes(income_ver, instance.calculator_kungfu_id)
    instance.income_list = income_code
    instance.income_ver = income_ver
    instance.formation_list = FORMATIONS[formation_ver]
    instance.formation_name = formation_ver
    return is_custom


async def _prepare_calculator_loop_selection(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    instance: UniversalCalculator | JX3BOXCalculator,
) -> None:
    is_custom = _apply_calculator_preferences(event, instance)
    loop_entries = await _calculator_loop_entries(instance, event.user_id, is_custom)
    if isinstance(loop_entries, str):
        await matcher.finish(loop_entries)
    state["loops"] = loop_entries
    state["instance"] = instance
    await matcher.send(_format_calculator_loop_selection(loop_entries))


async def _prepare_equip_compare_equipment_selection(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    instance: JX3PlayerAttribute,
    equip_name: str,
) -> None:
    kungfu_id = instance.kungfu_id
    current_jcl_line = instance.equip_lines
    currnet_dps_data = UniversalCalculator(current_jcl_line, int(str(kungfu_id)))

    income_ver = Preference(event.user_id, "", "").setting("计算器增益")
    formation_ver = Preference(event.user_id, "", "").setting("计算器阵眼")
    income_code = get_calculator_income_codes(income_ver, int(str(kungfu_id)))
    formation_code = FORMATIONS[formation_ver]

    currnet_dps_data.income_list = income_code
    currnet_dps_data.income_ver = income_ver
    currnet_dps_data.formation_list = formation_code
    currnet_dps_data.formation_name = formation_ver

    equips = await get_equip_list(equip_name)
    if not equips:
        await matcher.finish(f"未找到装备「{equip_name}」，请检查装备名，或尝试输入更完整的装备名称。")
    msg = "请从下面选择装备进行对比！"
    for index, equip_info in enumerate(equips, start=1):
        msg += f"\n{index}. ({equip_info.subkind}) {equip_info.name}\n{equip_info.quality} {' '.join(equip_info.attr)}"
    state["equips"] = equips
    state["kungfu_id"] = kungfu_id
    state["current_data"] = currnet_dps_data
    state["current_jcl"] = current_jcl_line
    await matcher.send(msg)


def _format_timeline_loop_selection(entries: list[dict[str, Any]], *, compare: bool, kline: bool = False) -> str:
    if compare:
        msg = "请选择要对比的计算循环，支持空格或逗号分隔！"
    elif kline:
        msg = "请选择要生成K线的计算循环！"
    else:
        msg = "请选择计算循环！"
    return _format_calculator_loop_selection(entries, msg)


async def _prepare_timeline_selection(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    args: Message,
    cmd: str,
    *,
    compare: bool,
    kline: bool = False,
) -> None:
    raw_text = args.extract_plain_text().strip()
    if raw_text == "":
        if kline:
            await matcher.finish(TIMELINE_KLINE_HELP_TEXT)
        if compare:
            await matcher.finish(TIMELINE_COMPARE_HELP_TEXT)
        await matcher.finish(TIMELINE_HELP_TEXT)
    if kline and raw_text.lower() in {"help", "帮助", "参数", "示例"}:
        await matcher.finish(TIMELINE_KLINE_HELP_TEXT)
    if not compare and not kline and raw_text.lower() in {"help", "帮助", "参数", "示例"}:
        await matcher.finish(TIMELINE_HELP_TEXT)
    if compare and raw_text.lower() in {"help", "帮助", "参数", "示例"}:
        await matcher.finish(TIMELINE_COMPARE_HELP_TEXT)
    arg, bin_size = _parse_timeline_command_args(raw_text)
    if isinstance(bin_size, str):
        await matcher.finish(bin_size)
    if compare and len(arg) not in [1, 2]:
        await matcher.finish(TIMELINE_COMPARE_HELP_TEXT)
    state["timeline_compare"] = compare
    state["timeline_kline"] = kline
    state["timeline_bin_size"] = bin_size
    instance = await _resolve_timeline_instance(event, matcher, state, arg, cmd)
    if instance is None:
        return
    await _prepare_timeline_loop_selection(
        event,
        matcher,
        state,
        instance,
        compare=compare,
        kline=kline,
        bin_size=bin_size,
    )


def _parse_timeline_selection(text: str, loop_count: int, *, compare: bool) -> list[int] | str:
    parts = [part for part in re.split(r"[\s,，]+", text.strip()) if part]
    if compare:
        if len(parts) < 2:
            return "循环对比至少需要选择 2 个循环，请重新发起命令！"
    elif len(parts) != 1:
        return "循环曲线只能选择 1 个循环，请重新发起命令！"
    results: list[int] = []
    for part in parts:
        if not check_number(part):
            return "循环选择有误，请重新发起命令！"
        index = int(part)
        if index < 1 or index > loop_count:
            return "超出可选范围，请重新发起命令！"
        if index not in results:
            results.append(index)
    if compare and len(results) < 2:
        return "循环对比至少需要选择 2 个不同循环，请重新发起命令！"
    return results


async def _request_damage_timeline(
    instance: UniversalCalculator | JX3BOXCalculator,
    loops: list[dict[str, Any]],
    selected_indices: list[int],
    user_id: int,
    bin_size: float,
    rolling_window: float,
) -> dict[str, Any] | str:
    selected_loops = []
    for index in selected_indices:
        loop_entry = loops[index - 1]
        selected_loops.append(
            {
                "name": loop_entry.get("display_name", ""),
                "index": index,
                "weapon": loop_entry.get("weapon", ""),
                "haste": loop_entry.get("haste", ""),
                "loop": loop_entry.get("loop", ""),
                "user_id": loop_entry.get("user_id", user_id),
            }
        )
    jcl_data = instance.jcl_data if getattr(instance, "jcl_data", None) else instance.equip_data.equip_lines
    kungfu_id = instance.calculator_kungfu_id
    payload = {
        "kungfu_id": kungfu_id,
        "jcl_data": normalize_calculator_jcl_data(jcl_data),
        "loops": selected_loops,
        "full_income": instance.income_list + instance.formation_list,
        "user_id": user_id,
        "bin_size": bin_size,
        "rolling_window": rolling_window,
    }
    try:
        response = await Request(f"{Config.jx3.api.calculator_url}/damage_timeline", params=payload).post(timeout=120)
        result = response.json()
    except Exception as exc:
        return f"循环曲线计算失败：{exc}"
    if result.get("code") != 200:
        return str(result.get("msg") or "循环曲线计算失败。")
    return result["data"]


def _rolling_kline_svg(
    series: dict[str, Any],
    width: int,
    main_height: int,
    volume_height: int,
    buff_overlays: list[dict[str, Any]] | None = None,
) -> str:
    adjusted = series.get("adjusted") or {}
    candles = adjusted.get("rolling_dps_candles") or []
    if not candles:
        return ""

    def number(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def merge_group(group: list[dict[str, Any]]) -> dict[str, Any]:
        first = group[0]
        last = group[-1]
        start_second = max(0.0, number(first.get("second")) - 1)
        end_second = number(last.get("second"))
        open_value = number(first.get("open"))
        close_value = number(last.get("close"))
        return {
            "second": end_second,
            "display_second": (start_second + end_second) / 2,
            "open": open_value,
            "close": close_value,
            "high": max(number(item.get("high")) for item in group),
            "low": min(number(item.get("low")) for item in group),
            "delta": close_value - open_value,
            "volume": sum(number(item.get("volume")) for item in group),
        }

    def display_candles(source_candles: list[dict[str, Any]], interval: int) -> list[dict[str, Any]]:
        ordered = sorted(source_candles, key=lambda item: number(item.get("second")))
        if interval <= 1:
            for item in ordered:
                item.setdefault("display_second", max(0.0, number(item.get("second")) - 0.5))
            return ordered
        grouped: list[dict[str, Any]] = []
        current_group: list[dict[str, Any]] = []
        current_index: int | None = None
        for item in ordered:
            second = max(1, int(number(item.get("second")) or 1))
            group_index = (second - 1) // interval
            if current_index is not None and group_index != current_index and current_group:
                grouped.append(merge_group(current_group))
                current_group = []
            current_index = group_index
            current_group.append(item)
        if current_group:
            grouped.append(merge_group(current_group))
        return grouped

    def display_interval(source_candles: list[dict[str, Any]]) -> int:
        if len(source_candles) <= DEFAULT_DAMAGE_TIMELINE_KLINE_TARGET_CANDLES:
            return 1
        raw_interval = math.ceil(len(source_candles) / DEFAULT_DAMAGE_TIMELINE_KLINE_TARGET_CANDLES)
        for interval in [2, 3, 5, 10, 15, 20, 30, 60]:
            if raw_interval <= interval:
                return interval
        return raw_interval

    rolling_window = max(0.1, number(adjusted.get("rolling_window") or DEFAULT_DAMAGE_TIMELINE_ROLLING_WINDOW))
    ordered_source_candles = sorted(candles, key=lambda item: number(item.get("second")))
    kline_interval = display_interval(ordered_source_candles)
    candles = display_candles(ordered_source_candles, kline_interval)
    terminal_second = max(
        max((number(item.get("second")) for item in candles), default=0),
        number(adjusted.get("battle_time")),
        1,
    )
    price_values = []
    for item in candles:
        price_values.extend(
            [
                number(item.get("open")),
                number(item.get("close")),
                number(item.get("high")),
                number(item.get("low")),
            ]
        )
    price_min = max(0, min(price_values, default=0) * 0.96)
    price_max = max(price_values, default=1) * 1.04
    if price_max <= price_min:
        price_max = price_min + 1
    price_span = price_max - price_min
    gap = 26
    total_height = main_height + gap + volume_height
    momentum_top = main_height + gap
    momentum_base = momentum_top + volume_height / 2
    momentum_bottom = momentum_top + volume_height
    max_momentum = max(
        (
            abs(number(item.get("delta", number(item.get("close")) - number(item.get("open")))))
            for item in candles
        ),
        default=1,
    )
    max_momentum = max(max_momentum, 1)

    def x_for_second(second: float) -> float:
        return second / terminal_second * width

    def price_y(value: float) -> float:
        return main_height - (value - price_min) / price_span * main_height

    def momentum_y(value: float) -> float:
        return momentum_base - value / max_momentum * (volume_height / 2)

    grid_lines = []
    for ratio in [0, 0.25, 0.5, 0.75, 1]:
        y = main_height - ratio * main_height
        value = price_min + price_span * ratio
        grid_lines.append(
            f'<line x1="0" y1="{y:.2f}" x2="{width}" y2="{y:.2f}" class="kline-grid"/>'
            f'<text x="-12" y="{y + 4:.2f}" text-anchor="end" class="kline-axis-label">{html.escape(_format_compact_number(value))}</text>'
        )
    grid_lines.append(
        f'<line x1="0" y1="{main_height + gap:.2f}" x2="{width}" y2="{main_height + gap:.2f}" class="kline-grid"/>'
        f'<line x1="0" y1="{momentum_base:.2f}" x2="{width}" y2="{momentum_base:.2f}" class="kline-zero-axis"/>'
        f'<line x1="0" y1="{momentum_bottom:.2f}" x2="{width}" y2="{momentum_bottom:.2f}" class="kline-axis"/>'
        f'<text x="-12" y="{momentum_base + 4:.2f}" text-anchor="end" class="kline-axis-label">涨跌</text>'
    )

    tick_seconds = []
    tick = 0
    while tick < terminal_second:
        tick_seconds.append(float(tick))
        tick += 15
    terminal_tick_x = x_for_second(terminal_second)
    tick_seconds = [
        tick_second
        for tick_second in tick_seconds
        if abs(x_for_second(tick_second) - terminal_tick_x) >= 54
    ]
    if not any(abs(tick_second - terminal_second) < 0.05 for tick_second in tick_seconds):
        tick_seconds.append(terminal_second)
    axis_ticks = []
    for tick_second in tick_seconds:
        x = x_for_second(tick_second)
        anchor = "middle"
        if x < 12:
            anchor = "start"
        elif x > width - 12:
            anchor = "end"
        axis_ticks.append(
            f'<line x1="{x:.2f}" y1="{momentum_bottom:.2f}" x2="{x:.2f}" y2="{momentum_bottom + 7:.2f}" class="kline-axis"/>'
            f'<text x="{x:.2f}" y="{momentum_bottom + 24:.2f}" text-anchor="{anchor}" class="kline-axis-label">{html.escape(_format_seconds(tick_second))}</text>'
        )

    overlay_bands = _buff_overlays_svg(buff_overlays or [], width, main_height, terminal_second)
    candle_slot_width = width / max(1, terminal_second / kline_interval)
    candle_width = max(4.8, min(14, candle_slot_width * 0.58))
    candles_svg = []
    volume_svg = []
    ma_points_by_period: dict[int, list[tuple[float, float]]] = {
        period: [] for period in DEFAULT_DAMAGE_TIMELINE_KLINE_MA_PERIODS
    }
    ordered_candles = sorted(candles, key=lambda item: number(item.get("second")))
    close_values: list[float] = []
    for item in ordered_candles:
        second = number(item.get("second"))
        open_value = number(item.get("open"))
        close_value = number(item.get("close"))
        high_value = number(item.get("high"))
        low_value = number(item.get("low"))
        delta_value = number(item.get("delta", close_value - open_value))
        close_values.append(close_value)
        color = "#EF4444" if close_value >= open_value else "#22C55E"
        x = x_for_second(number(item.get("display_second", max(0.0, second - 0.5))))
        for period in DEFAULT_DAMAGE_TIMELINE_KLINE_MA_PERIODS:
            ma_start = max(0, len(close_values) - period)
            ma_value = sum(close_values[ma_start:]) / (len(close_values) - ma_start)
            ma_points_by_period[period].append((x, price_y(ma_value)))
        y_open = price_y(open_value)
        y_close = price_y(close_value)
        y_high = price_y(high_value)
        y_low = price_y(low_value)
        body_height = abs(y_close - y_open)
        if body_height < 1.4:
            body_y = y_open - 0.7
            body_height = 1.4
        else:
            body_y = min(y_open, y_close)
        candles_svg.append(
            f'<line x1="{x:.2f}" y1="{y_high:.2f}" x2="{x:.2f}" y2="{y_low:.2f}" stroke="{color}" stroke-width="1.8"/>'
            f'<rect x="{x - candle_width / 2:.2f}" y="{body_y:.2f}" width="{candle_width:.2f}" height="{body_height:.2f}" '
            f'rx="1" fill="{color}" fill-opacity="0.28" stroke="{color}" stroke-width="1.8"/>'
        )
        y_delta = momentum_y(delta_value)
        bar_y = min(momentum_base, y_delta)
        bar_height = max(1.0, abs(momentum_base - y_delta))
        volume_svg.append(
            f'<rect x="{x - candle_width / 2:.2f}" y="{bar_y:.2f}" width="{candle_width:.2f}" '
            f'height="{bar_height:.2f}" fill="{color}" fill-opacity="0.58"/>'
        )

    ma_classes = {5: "ma5", 10: "ma10", 20: "ma20"}
    ma_svg_parts = []
    for period in DEFAULT_DAMAGE_TIMELINE_KLINE_MA_PERIODS:
        ma_points = ma_points_by_period.get(period, [])
        if len(ma_points) < 2:
            continue
        ma_path = " ".join(f"{x:.2f},{y:.2f}" for x, y in ma_points)
        label_x, label_y = ma_points[-1]
        ma_class = ma_classes.get(period, "ma")
        ma_svg_parts.append(
            f'<polyline points="{ma_path}" fill="none" class="kline-ma-line {ma_class}"/>'
            f'<text x="{min(width + 8, label_x + 8):.2f}" y="{label_y + 4 + (period // 5 - 1) * 14:.2f}" '
            f'class="kline-ma-label {ma_class}">MA{period}</text>'
        )
    ma_svg = "".join(ma_svg_parts)

    if series.get("game_mode"):
        title = f"价格K线 · {rolling_window:g}秒滚动DPS"
        subtitle = f"最近{_format_seconds(terminal_second)} · {kline_interval}秒K · 红涨绿跌 · MA5/MA10/MA20均价线 · 底部为Close-Open"
    else:
        label = html.escape(str(series.get("label") or "A"))
        loop_name = html.escape(str(series.get("loop_name") or "未命名循环"))
        title = f"循环K线 · {rolling_window:g}秒滚动DPS"
        subtitle = (
            f"{label}. {loop_name} · {kline_interval}秒K · "
            "红涨绿跌 · MA5/MA10/MA20均价线 · 底部为Close-Open"
        )
    return (
        f'<div class="chart-title kline-heading">{html.escape(title)}</div>'
        f'<div class="kline-subtitle">{subtitle}</div>'
        f'<svg viewBox="-78 -28 {width + 160} {total_height + 64}" class="kline-chart">'
        + "".join(grid_lines)
        + overlay_bands
        + "".join(candles_svg)
        + ma_svg
        + "".join(volume_svg)
        + f'<line x1="0" y1="{main_height}" x2="{width}" y2="{main_height}" class="kline-axis"/>'
        + "".join(axis_ticks)
        + '</svg>'
    )


async def _render_damage_timeline_image(
    data: dict[str, Any],
    instance: UniversalCalculator | JX3BOXCalculator,
    *,
    compare: bool,
    kline_only: bool = False,
) -> Any:
    series_list = data.get("series") or []
    colors = ["#2F6BFF", "#E05252", "#18A058", "#8B5CF6", "#F59E0B", "#0EA5A4"]
    name, server = getattr(instance, "info", ("", ""))
    kungfu = Kungfu.with_internel_id(instance.calculator_kungfu_id, convert_to_pc=True)
    title = "循环K线" if kline_only else ("循环对比" if compare else "循环曲线")
    if data.get("title"):
        title = str(data["title"])
    game_stats = data.get("game_stats") or {}
    game_mode = kline_only and bool(game_stats)
    legend_items = []
    stat_cards = []
    for index, series in enumerate(series_list):
        color = colors[index % len(colors)]
        adjusted = series.get("adjusted") or {}
        dps = _format_compact_number(adjusted.get("dps"))
        label = html.escape(str(series.get("label") or index + 1))
        loop_name = html.escape(str(series.get("loop_name") or "未命名循环"))
        if game_mode:
            legend_items.append(f'<span class="legend-item"><i style="background:{color}"></i>标的价格</span>')
            stat_cards.append(
                f'<div class="stat-card" style="border-left-color:{color}">'
                f'<div class="stat-title">期权账户</div>'
                f'<div class="stat-grid">'
                f'<span>现金 <b>{html.escape(str(game_stats.get("cash", "-")))}</b></span>'
                f'<span>价格 <b>{html.escape(str(game_stats.get("price", "-")))}</b></span>'
                f'<span>时间 <b>{html.escape(str(game_stats.get("time", "-")))}</b></span>'
                f'<span>本轮T <b>{html.escape(str(game_stats.get("term", "-")))}</b></span>'
                f'<span>到期 <b>{html.escape(str(game_stats.get("expiry", "-")))}</b></span>'
                f'<span>持仓 <b>{html.escape(str(game_stats.get("positions", "-")))}</b></span>'
                f'</div></div>'
            )
            continue
        legend_items.append(f'<span class="legend-item"><i style="background:{color}"></i>{label}. {loop_name}</span>')
        stat_cards.append(
            f'<div class="stat-card" style="border-left-color:{color}">'
            f'<div class="stat-title">{label}. {loop_name}</div>'
            f'<div class="stat-grid">'
            f'<span>DPS <b>{dps}</b></span>'
            f'<span>总伤 <b>{html.escape(_format_compact_number(adjusted.get("total_damage")))}</b></span>'
            f'<span>时长 <b>{adjusted.get("battle_time", 0)}s</b></span>'
            f'<span>加速 <b>{html.escape(str(series.get("haste") or "-"))}</b></span>'
            f'</div></div>'
        )
    chart_width = 900
    chart_height = 300
    bin_size = float(data.get("bin_size", 1) or 1)
    buff_overlays = data.get("buff_overlays") or []
    if getattr(instance, "income_ver", "") not in FULL_INCOME_WITH_CONSUMABLES:
        buff_overlays = []
    kline_chart = ""
    if kline_only and len(series_list) == 1:
        kline_chart = _rolling_kline_svg(series_list[0], chart_width, 300, 86, buff_overlays)
    damage_title = f"每{bin_size:g}秒伤害量" if bin_size != 1 else "每秒伤害量"
    damage_chart = _chart_svg(
        series_list,
        "damage_per_second_bin",
        colors,
        damage_title,
        chart_width,
        chart_height,
        True,
        buff_overlays=buff_overlays,
    )
    dps_chart = _chart_svg(
        series_list,
        "cumulative_dps",
        colors,
        "累计实时 DPS",
        chart_width,
        chart_height,
        False,
        source_key="cumulative_dps_bins",
        buff_overlays=buff_overlays,
    )
    body_class = "kline-page" if kline_only else ""
    canvas_class = "canvas kline-mode" if kline_only else "canvas"
    subtitle_text = (
        f"{html.escape(server or '-')} · {html.escape(name or '-')} · {html.escape(kungfu.name or '未知心法')}"
    )
    badge_text = f"{html.escape(instance.income_ver or '无增益')} / {html.escape(instance.formation_name or '无阵眼')}"
    if game_mode:
        subtitle_text = "期权模拟 · 标的：滚动DPS收盘价 · T随机15/30/45/60s · 权利金3%"
        badge_text = "看涨 / 看跌 / 自动行权"
    html_source = Template(calculator_timeline_template).render(
        value_0=body_class,
        value_1=canvas_class,
        value_2=html.escape(title),
        value_3=subtitle_text,
        value_4=badge_text,
        value_5=''.join(legend_items),
        value_6=''.join(stat_cards),
        value_7=f'<div class="panel kline-panel">{kline_chart}</div>' if kline_chart else '',
        value_8='' if kline_only else f'<div class="panel">{damage_chart}</div>',
        value_9='' if kline_only else f'<div class="panel">{dps_chart}</div>',
    )
    return await generate(
        html_source,
        ".canvas",
        False,
        segment=True,
        full_screen=True,
        viewport={"width": 1100, "height": 1120 if kline_only else 1500},
    )


async def _request_kline_game_random_jcl() -> dict[str, Any] | str:
    payload = {
        "bin_size": DEFAULT_DAMAGE_TIMELINE_BIN_SIZE,
        "rolling_window": DEFAULT_DAMAGE_TIMELINE_ROLLING_WINDOW,
    }
    try:
        result = (
            await Request(
                f"{Config.jx3.api.calculator_url}/kline_game_random_jcl",
                params=payload,
            ).post(timeout=120)
        ).json()
    except Exception as exc:
        return f"K线游戏随机 JCL 获取失败：{exc}"
    if result.get("code") != 200:
        return str(result.get("msg") or "K线游戏随机 JCL 获取失败。")
    return result["data"]


def _kline_game_price_at(game: dict[str, Any], second: int) -> float:
    candles = game.get("candles") or []
    if not candles:
        return 0
    selected = candles[0]
    for candle in candles:
        if int(candle.get("second", 0) or 0) > second:
            break
        selected = candle
    return float(selected.get("close", 0) or 0)


def _kline_game_end_second(game: dict[str, Any]) -> int:
    candles = game.get("candles") or []
    if not candles:
        return 0
    return int(candles[-1].get("second", 0) or 0)


def _kline_game_roll_option_t() -> int:
    return random.choice(KLINE_GAME_OPTION_TERMS)


def _kline_game_current_option_t(game: dict[str, Any]) -> int:
    try:
        option_t = int(game.get("option_t", 0) or 0)
    except (TypeError, ValueError):
        option_t = 0
    if option_t not in KLINE_GAME_OPTION_TERMS:
        option_t = _kline_game_roll_option_t()
        game["option_t"] = option_t
    return option_t


async def _kline_game_append_segment(game: dict[str, Any]) -> str | None:
    data = await _request_kline_game_random_jcl()
    if isinstance(data, str):
        return data
    series_list = data.get("series") or []
    if not series_list:
        return "K线游戏随机 JCL 没有返回可用曲线。"
    series = series_list[0]
    adjusted = series.get("adjusted") or {}
    source_candles = adjusted.get("rolling_dps_candles") or []
    if not source_candles:
        return "K线游戏随机 JCL 没有可用 K 线数据。"
    offset = _kline_game_end_second(game)
    appended = []
    for candle in source_candles:
        item = dict(candle)
        item["second"] = offset + int(float(item.get("second", 0) or 0))
        appended.append(item)
    game.setdefault("candles", []).extend(appended)
    source = data.get("source") or {}
    source["start_second"] = offset
    source["end_second"] = _kline_game_end_second(game)
    game.setdefault("sources", []).append(source)
    game["kungfu_id"] = int(source.get("kungfu_id") or game.get("kungfu_id") or 0)
    game["last_source"] = source
    return None


async def _kline_game_ensure_future(game: dict[str, Any], target_second: int) -> str | None:
    attempts = 0
    while _kline_game_end_second(game) < target_second and attempts < 8:
        error = await _kline_game_append_segment(game)
        if error:
            return error
        attempts += 1
    if _kline_game_end_second(game) < target_second:
        return "K线游戏拼接随机 JCL 失败：可用数据长度不足。"
    return None


async def _new_kline_game() -> dict[str, Any] | str:
    game: dict[str, Any] = {
        "cash": float(KLINE_GAME_INITIAL_CASH),
        "positions": [],
        "candles": [],
        "sources": [],
        "round": 1,
        "option_t": _kline_game_roll_option_t(),
    }
    error = await _kline_game_ensure_future(
        game,
        KLINE_GAME_MIN_HISTORY + KLINE_GAME_MIN_REMAINING + max(KLINE_GAME_OPTION_TERMS),
    )
    if error:
        return error
    end_second = _kline_game_end_second(game)
    latest_start = max(KLINE_GAME_MIN_HISTORY, end_second - KLINE_GAME_MIN_REMAINING)
    game["current_time"] = random.randint(KLINE_GAME_MIN_HISTORY, latest_start)
    return game


def _kline_game_position_summary(game: dict[str, Any]) -> str:
    positions = [pos for pos in game.get("positions", []) if int(pos.get("quantity", 0) or 0) > 0]
    if not positions:
        return "无"
    call_count = sum(int(pos.get("quantity", 0) or 0) for pos in positions if pos.get("type") == "call")
    put_count = sum(int(pos.get("quantity", 0) or 0) for pos in positions if pos.get("type") == "put")
    parts = []
    if call_count:
        parts.append(f"看涨{call_count}")
    if put_count:
        parts.append(f"看跌{put_count}")
    return " ".join(parts) or "无"


async def _render_kline_game_image(game: dict[str, Any]) -> Any:
    current_time = int(game.get("current_time", 0) or 0)
    option_t = _kline_game_current_option_t(game)
    history_start = max(0, current_time - KLINE_GAME_HISTORY_WINDOW)
    history = [
        {
            **dict(candle),
            "second": int(candle.get("second", 0) or 0) - history_start,
        }
        for candle in (game.get("candles") or [])
        if history_start < int(candle.get("second", 0) or 0) <= current_time
    ]
    display_duration = min(current_time, KLINE_GAME_HISTORY_WINDOW)
    current_price = _kline_game_price_at(game, current_time)
    data = {
        "title": "循环K线游戏",
        "game_stats": {
            "cash": _format_compact_number(game.get("cash", 0)),
            "price": _format_compact_number(current_price),
            "time": f"{current_time}s",
            "term": f"{option_t}s",
            "expiry": f"{current_time + option_t}s",
            "positions": _kline_game_position_summary(game),
        },
        "series": [
            {
                "label": "PRICE",
                "loop_name": "滚动DPS收盘价",
                "haste": "-",
                "game_mode": True,
                "adjusted": {
                    "rolling_window": DEFAULT_DAMAGE_TIMELINE_ROLLING_WINDOW,
                    "battle_time": display_duration,
                    "dps": current_price,
                    "total_damage": game.get("cash", 0),
                    "rolling_dps_candles": history,
                },
            }
        ],
    }
    instance = UniversalCalculator(
        jcl_data=[],
        kungfu_id=0,
        info=("K线游戏", "期权模拟"),
    )
    instance.income_ver = "期权模拟"
    instance.formation_name = "自动行权"
    return await _render_damage_timeline_image(data, instance, compare=False, kline_only=True)


def _kline_game_prompt(game: dict[str, Any], note: str = "") -> str:
    current_time = int(game.get("current_time", 0) or 0)
    option_t = _kline_game_current_option_t(game)
    current_price = _kline_game_price_at(game, current_time)
    premium = current_price * KLINE_GAME_PREMIUM_RATE
    expiry = current_time + option_t
    lines = []
    if note:
        lines.append(note)
    lines.extend(
        [
            f"当前时间：{current_time}s，标的价格：{_format_compact_number(current_price)}",
            f"现金：{_format_compact_number(game.get('cash', 0))}，持仓：{_kline_game_position_summary(game)}",
            f"本轮平值期权：K={_format_compact_number(current_price)}，T={option_t}s，权利金={_format_compact_number(premium)}/张，到期={expiry}s",
            "操作：买入看涨 <数量> / 买入看跌 <数量> / 卖出看涨 <数量> / 卖出看跌 <数量> / 不动 / 结束",
        ]
    )
    return "\n".join(lines)


async def _send_kline_game_state(matcher: Matcher, game: dict[str, Any], note: str = "") -> None:
    await matcher.send(await _render_kline_game_image(game))
    await matcher.send(_kline_game_prompt(game, note))


def _parse_kline_game_action(text: str) -> dict[str, Any] | str:
    cleaned = text.strip()
    lowered = cleaned.lower()
    if lowered in {"结束", "退出", "quit", "exit", "stop"}:
        return {"action": "quit"}
    if lowered in {"不动", "pass", "hold", "跳过"}:
        return {"action": "hold"}
    parts = cleaned.split()
    if not parts:
        return "请输入操作：买入看涨 <数量> / 买入看跌 <数量> / 不动 / 结束"
    quantity = 1
    if len(parts) >= 2:
        quantity_text = parts[-1]
        if quantity_text.isdecimal():
            quantity = int(quantity_text)
            option_text = "".join(parts[:-1])
        elif check_number(quantity_text):
            return "数量必须为正整数。"
        else:
            option_text = "".join(parts)
    else:
        option_text = "".join(parts)
    if quantity <= 0:
        return "数量必须为正整数。"
    action = ""
    if option_text.startswith(("买入", "买")):
        action = "buy"
    elif option_text.startswith(("卖出", "卖")):
        action = "sell"
    else:
        return "操作格式有误：请使用 买入看涨 <数量> / 买入看跌 <数量> / 卖出看涨 <数量> / 卖出看跌 <数量> / 不动。"
    if "看涨" in option_text or "买涨" in option_text or "卖涨" in option_text or "call" in lowered:
        option_type = "call"
    elif "看跌" in option_text or "买跌" in option_text or "卖跌" in option_text or "put" in lowered:
        option_type = "put"
    else:
        return "请指定看涨或看跌。"
    return {"action": action, "type": option_type, "quantity": quantity}


def _is_kline_game_format_error(result: str | None) -> bool:
    if not isinstance(result, str):
        return False
    return result.startswith(("请输入", "操作格式", "请指定", "数量"))


def _kline_game_option_mark_price(position: dict[str, Any], current_price: float, current_time: int) -> float:
    strike = float(position.get("strike", 0) or 0)
    expires_at = int(position.get("expires_at", current_time) or current_time)
    opened_at = int(position.get("opened_at", current_time) or current_time)
    term = int(position.get("term", expires_at - opened_at) or (expires_at - opened_at) or min(KLINE_GAME_OPTION_TERMS))
    term = max(1, term)
    remaining = max(0, expires_at - current_time)
    if position.get("type") == "call":
        intrinsic = max(current_price - strike, 0)
    else:
        intrinsic = max(strike - current_price, 0)
    time_value = current_price * KLINE_GAME_PREMIUM_RATE * min(1, remaining / term)
    return intrinsic + time_value


def _kline_game_buy(game: dict[str, Any], option_type: str, quantity: int) -> str | None:
    current_time = int(game.get("current_time", 0) or 0)
    option_t = _kline_game_current_option_t(game)
    current_price = _kline_game_price_at(game, current_time)
    premium = current_price * KLINE_GAME_PREMIUM_RATE
    cost = premium * quantity
    cash = float(game.get("cash", 0) or 0)
    if cash < cost:
        return f"现金不足：需要 {_format_compact_number(cost)}，当前只有 {_format_compact_number(cash)}。"
    game["cash"] = cash - cost
    game.setdefault("positions", []).append(
        {
            "type": option_type,
            "quantity": quantity,
            "strike": current_price,
            "premium": premium,
            "term": option_t,
            "opened_at": current_time,
            "expires_at": current_time + option_t,
        }
    )
    return None


def _kline_game_sell(game: dict[str, Any], option_type: str, quantity: int) -> str | None:
    current_time = int(game.get("current_time", 0) or 0)
    current_price = _kline_game_price_at(game, current_time)
    available_total = sum(
        int(position.get("quantity", 0) or 0)
        for position in game.get("positions", [])
        if position.get("type") == option_type and int(position.get("expires_at", 0) or 0) > current_time
    )
    if available_total < quantity:
        return "当前没有足够的未到期持仓可卖出，不能裸卖空。"
    remaining_quantity = quantity
    cash_gain = 0.0
    for position in list(game.get("positions", [])):
        if remaining_quantity <= 0:
            break
        if position.get("type") != option_type or int(position.get("expires_at", 0) or 0) <= current_time:
            continue
        available = int(position.get("quantity", 0) or 0)
        if available <= 0:
            continue
        sell_quantity = min(available, remaining_quantity)
        cash_gain += _kline_game_option_mark_price(position, current_price, current_time) * sell_quantity
        position["quantity"] = available - sell_quantity
        remaining_quantity -= sell_quantity
    game["positions"] = [pos for pos in game.get("positions", []) if int(pos.get("quantity", 0) or 0) > 0]
    game["cash"] = float(game.get("cash", 0) or 0) + cash_gain
    return None


def _kline_game_settle(game: dict[str, Any]) -> str:
    current_time = int(game.get("current_time", 0) or 0)
    current_price = _kline_game_price_at(game, current_time)
    remaining_positions = []
    messages = []
    for position in game.get("positions", []):
        quantity = int(position.get("quantity", 0) or 0)
        if quantity <= 0:
            continue
        expires_at = int(position.get("expires_at", 0) or 0)
        if expires_at > current_time:
            remaining_positions.append(position)
            continue
        strike = float(position.get("strike", 0) or 0)
        premium = float(position.get("premium", 0) or 0)
        if position.get("type") == "call":
            payoff_per = max(current_price - strike, 0)
            name = "看涨"
        else:
            payoff_per = max(strike - current_price, 0)
            name = "看跌"
        payoff = payoff_per * quantity
        net = payoff - premium * quantity
        game["cash"] = float(game.get("cash", 0) or 0) + payoff
        term = int(position.get("term", expires_at - int(position.get("opened_at", 0) or 0)) or 0)
        term_text = f"，T={term}s" if term > 0 else ""
        if payoff > 0:
            exercise_text = f"行权收入={_format_compact_number(payoff)}"
        else:
            exercise_text = "放弃行权，行权收入=0"
        messages.append(
            f"{name}{quantity}张到期{term_text}：K={_format_compact_number(strike)}，"
            f"到期价={_format_compact_number(current_price)}，{exercise_text}，"
            f"净收益={_format_compact_number(net)}"
        )
    game["positions"] = remaining_positions
    return "\n".join(messages) if messages else "本轮无到期期权。"


async def _kline_game_apply_action(game: dict[str, Any], action_text: str) -> str | None:
    parsed = _parse_kline_game_action(action_text)
    if isinstance(parsed, str):
        return parsed
    if parsed["action"] == "quit":
        return "quit"
    current_time = int(game.get("current_time", 0) or 0)
    option_t = _kline_game_current_option_t(game)
    target_second = current_time + option_t + KLINE_GAME_MIN_REMAINING
    error = await _kline_game_ensure_future(game, target_second)
    if error:
        return error
    note = ""
    if parsed["action"] == "buy":
        error = _kline_game_buy(game, parsed["type"], int(parsed["quantity"]))
        if error:
            return error
        option_name = "看涨" if parsed["type"] == "call" else "看跌"
        note = f"已买入{option_name}{parsed['quantity']}张。"
    elif parsed["action"] == "sell":
        error = _kline_game_sell(game, parsed["type"], int(parsed["quantity"]))
        if error:
            return error
        option_name = "看涨" if parsed["type"] == "call" else "看跌"
        note = f"已卖出{option_name}{parsed['quantity']}张。"
    elif parsed["action"] == "hold":
        note = "本轮选择不动。"
    game["current_time"] = current_time + option_t
    settlement = _kline_game_settle(game)
    game["round"] = int(game.get("round", 1) or 1) + 1
    game["option_t"] = _kline_game_roll_option_t()
    return note + "\n" + settlement


async def _finish_damage_timeline(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    selection: Message,
) -> None:
    if "timeline_kungfu_options" in state:
        num = selection.extract_plain_text()
        if not check_number(num):
            await matcher.finish("心法选择有误，请重新发起命令！")
        options: list[dict[str, Any]] = state["timeline_kungfu_options"]
        index = int(num)
        if index < 1 or index > len(options):
            await matcher.finish("超出可选范围，请重新发起命令！")
        selected_tag = str(options[index - 1]["tag"])
        context: dict[str, Any] = state["timeline_kungfu_context"]
        if context["mode"] == "global":
            candidate = await UniversalCalculator.with_global_role_id(int(context["global_role_id"]), selected_tag)
        else:
            candidate = await UniversalCalculator.with_name(str(context["name"]), str(context["server"]), selected_tag)
        if isinstance(candidate, str):
            await matcher.finish(candidate)
        instance = cast(UniversalCalculator, candidate)
        state.pop("timeline_kungfu_options", None)
        state.pop("timeline_kungfu_context", None)
        state.pop("timeline_loop_order", None)
        await _prepare_timeline_loop_selection(
            event,
            matcher,
            state,
            instance,
            compare=bool(state.get("timeline_compare")),
            kline=bool(state.get("timeline_kline")),
            bin_size=float(state.get("timeline_bin_size", DEFAULT_DAMAGE_TIMELINE_BIN_SIZE)),
        )
        await matcher.reject()

    if "timeline_loops" not in state or "timeline_instance" not in state:
        await matcher.finish("循环曲线/循环对比/循环K线状态已失效，请重新发起命令！")
    loops: list[dict[str, Any]] = state["timeline_loops"]
    instance: UniversalCalculator | JX3BOXCalculator = state["timeline_instance"]
    compare = bool(state.get("timeline_compare"))
    kline = bool(state.get("timeline_kline"))
    parsed = _parse_timeline_selection(selection.extract_plain_text(), len(loops), compare=compare)
    if isinstance(parsed, str):
        await matcher.finish(parsed)
    await matcher.send("正在演算中，请稍候……")
    user_id = event.user_id if state.get("timeline_is_custom") else 0
    bin_size = float(state.get("timeline_bin_size", DEFAULT_DAMAGE_TIMELINE_BIN_SIZE))
    rolling_window = DEFAULT_DAMAGE_TIMELINE_ROLLING_WINDOW
    data = await _request_damage_timeline(instance, loops, parsed, user_id, bin_size, rolling_window)
    if isinstance(data, str):
        await matcher.finish(data)
    if state.get("timeline_pzid", 0) != 0:
        await matcher.send(ms.image(await get_equip_image(str(state["timeline_pzid"]))))
    await matcher.finish(await _render_damage_timeline_image(data, instance, compare=compare, kline_only=kline))


rd_analysis_support_matcher = on_command("jx3_rd_analysis_support", aliases={"RD分析支持", "rd分析支持", "Rd分析支持"}, priority=5, force_whitespace=True)


@rd_analysis_support_matcher.handle()
async def _():
    await rd_analysis_support_matcher.finish(RD_ANALYSIS_SUPPORT_TEXT)


jcl_analysis_help_matcher = on_command("jx3_jcl_analysis", aliases={"JCL分析", "jcl分析", "Jcl分析"}, priority=5, force_whitespace=True)


@jcl_analysis_help_matcher.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    query = args.extract_plain_text().strip().lower()
    if query not in {"", "help", "帮助", "参数", "示例"}:
        await matcher.finish("参考格式：JCL分析 help")
    await matcher.finish(_jcl_analysis_help_message())


custom_loop_help_matcher = on_command("jx3_custom_loop_help", aliases={"自定义循环"}, priority=5, force_whitespace=True)


@custom_loop_help_matcher.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    query = args.extract_plain_text().strip().lower()
    if query not in {"", "help", "帮助", "参数", "示例"}:
        await matcher.finish("参考格式：自定义循环 help")
    await matcher.finish(await _render_custom_loop_help_image())


calculator_support_matcher = on_command("jx3_calculator_support", aliases={"计算器支持", "计算器心法", "计算器支持心法"}, priority=5, force_whitespace=True)


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


equipment_rating_support_matcher = on_command("jx3_equipment_rating_support", aliases={"装备评级支持", "装备评级心法", "装备评级支持心法"}, priority=5, force_whitespace=True)


@equipment_rating_support_matcher.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    await equipment_rating_module.handle_equipment_rating_support(matcher, args)


equipment_rating_matcher = on_command("jx3_equipment_rating", aliases={"装备评级"}, priority=5, force_whitespace=True)


@equipment_rating_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg()):
    query = args.extract_plain_text().strip().lower()
    if query in {"help", "帮助", "参数", "示例", "?", "？"}:
        await matcher.finish(await equipment_rating_module._render_equipment_rating_help_image())
    await equipment_rating_module.handle_equipment_rating(event, matcher, state, args)


@equipment_rating_matcher.got("rating_jcl_order")
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, rating_jcl_order: Message = Arg()):
    await equipment_rating_module.handle_equipment_rating_loop_order(event, matcher, state, rating_jcl_order)


timeline_matcher = on_command(
    "jx3_damage_timeline",
    aliases=cast(Any, _prefixed_command_aliases("循环曲线", CALCULATOR_PREFIXES)),
    priority=5,
    force_whitespace=True,
)


@timeline_matcher.handle()
async def _(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    args: Message = CommandArg(),
    cmd: str = RawCommand(),
):
    await _prepare_timeline_selection(event, matcher, state, args, cmd, compare=False)


@timeline_matcher.got("timeline_loop_order")
async def _(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    timeline_loop_order: Message = Arg(),
):
    await _finish_damage_timeline(event, matcher, state, timeline_loop_order)


timeline_compare_matcher = on_command(
    "jx3_damage_timeline_compare",
    aliases=cast(Any, _prefixed_command_aliases("循环对比", CALCULATOR_PREFIXES)),
    priority=5,
    force_whitespace=True,
)


@timeline_compare_matcher.handle()
async def _(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    args: Message = CommandArg(),
    cmd: str = RawCommand(),
):
    await _prepare_timeline_selection(event, matcher, state, args, cmd, compare=True)


@timeline_compare_matcher.got("timeline_loop_order")
async def _(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    timeline_loop_order: Message = Arg(),
):
    await _finish_damage_timeline(event, matcher, state, timeline_loop_order)


timeline_kline_matcher = on_command(
    "jx3_damage_timeline_kline",
    aliases=cast(Any, (
        _prefixed_command_aliases("循环k线", CALCULATOR_PREFIXES)
        | _prefixed_command_aliases("循环K线", CALCULATOR_PREFIXES)
    )),
    priority=5,
    force_whitespace=True,
)


@timeline_kline_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg(), cmd: str = RawCommand()):
    await _prepare_timeline_selection(event, matcher, state, args, cmd, compare=False, kline=True)


@timeline_kline_matcher.got("timeline_loop_order")
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, timeline_loop_order: Message = Arg()):
    await _finish_damage_timeline(event, matcher, state, timeline_loop_order)


kline_game_matcher = on_command("jx3_damage_timeline_kline_game", aliases={"循环k线游戏", "循环K线游戏"}, priority=5, force_whitespace=True)


@kline_game_matcher.handle()
async def _(matcher: Matcher, state: T_State, args: Message = CommandArg()):
    query = args.extract_plain_text().strip().lower()
    if query in {"help", "帮助", "参数", "示例"}:
        await kline_game_matcher.finish(
            "循环K线游戏参数：\n"
            "发送「循环k线游戏」开始一局。\n"
            "初始资金 1,000,000；标的为 rolling DPS close；平值期权 K=当前价格；"
            "权利金=当前价格*3%；T 在 15/30/45/60 秒中随机生成，到期自动行权。\n"
            "操作：买入看涨 <数量> / 买入看跌 <数量> / 卖出看涨 <数量> / 卖出看跌 <数量> / 不动 / 结束"
        )
    if query:
        await kline_game_matcher.finish("参考格式：循环k线游戏")
    await matcher.send("正在随机抽取 JCL 并初始化 K线游戏。")
    game = await _new_kline_game()
    if isinstance(game, str):
        await kline_game_matcher.finish(game)
    state["kline_game"] = game
    await _send_kline_game_state(matcher, game, "游戏开始。")


@kline_game_matcher.got("kline_game_action")
async def _(matcher: Matcher, state: T_State, kline_game_action: Message = Arg()):
    game = state.get("kline_game")
    if not isinstance(game, dict):
        await kline_game_matcher.finish("K线游戏状态已失效，请重新发起命令。")
    action_text = kline_game_action.extract_plain_text().strip()
    result = await _kline_game_apply_action(game, action_text)
    if result == "quit":
        await kline_game_matcher.finish(
            f"已结束 K线游戏。\n最终现金：{_format_compact_number(game.get('cash', 0))}"
        )
    if _is_kline_game_format_error(result):
        game["format_error_streak"] = int(game.get("format_error_streak", 0) or 0) + 1
        state["kline_game"] = game
        if game["format_error_streak"] >= 3:
            await kline_game_matcher.finish(
                f"连续 3 次操作格式有误，K线游戏已自动退出。\n"
                f"最终现金：{_format_compact_number(game.get('cash', 0))}"
            )
        await matcher.reject(f"{result}\n连续格式错误：{game['format_error_streak']}/3")
    game["format_error_streak"] = 0
    if isinstance(result, str) and (
        result.startswith("现金不足")
        or result.startswith("当前没有足够")
        or result.startswith("K线游戏")
    ):
        state["kline_game"] = game
        await matcher.reject(result)
    state["kline_game"] = game
    await _send_kline_game_state(matcher, game, result or "")
    await matcher.reject("继续操作，或发送「结束」退出。")


therapy_panel_matcher = on_command("jx3_calculator_therapy_panel", aliases={"治疗面板"}, priority=5, force_whitespace=True)


@therapy_panel_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    usage = "参考格式：治疗面板 <服务器> <角色名>\n示例：治疗面板 梦江南 咩咩"
    query = args.extract_plain_text().strip()
    if query == "" or query.lower() in {"help"} or query in {"帮助", "参数", "示例"}:
        await therapy_panel_matcher.finish(usage)
    parts = [part for part in query.split() if part]
    if len(parts) != 2:
        await therapy_panel_matcher.finish(PROMPT.ArgumentCountInvalid + "\n" + usage)
    server = Server(parts[0], event.group_id).server
    if server is None:
        await therapy_panel_matcher.finish(PROMPT.ServerNotExist)
    await therapy_panel_matcher.finish(await therapy_panel(server, parts[1]))


calc_matcher = on_command("jx3_calculator", aliases={"计算器", "T计算器", "QC计算器", "JC计算器", "TL计算器", "JY计算器", "WX计算器"}, priority=5, force_whitespace=True)


@calc_matcher.handle()
async def _(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    args: Message = CommandArg(),
    cmd: str = RawCommand(),
):
    raw_text = args.extract_plain_text().strip()
    if raw_text.lower() in {"help"} or raw_text in {"帮助", "参数", "示例"}:
        await calc_matcher.finish(_calculator_help_message())
    if raw_text == "":
        matcher.stop_propagation()
        return
    raw_arg = raw_text.split(" ")
    arg = [a for a in raw_arg if a != "-A"]
    if len(arg) not in [1, 2]:
        await calc_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：计算器 <服务器> <角色名>\n计算器 <魔盒配装ID>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    else:
        server = arg[0]
        name = arg[1]
    state["pzid"] = 0
    tag = _calculator_tag_from_command(cmd)
    is_specific_calculator = _calculator_command_has_specific_prefix(cmd)
    if check_number(name):
        instance = await JX3BOXCalculator.with_pzid(int(name))
        if isinstance(instance, str):
            await calc_matcher.finish(instance)
        state["pzid"] = int(name)
    elif name.startswith("g"):
        global_role_id = name[1:]
        if not check_number(global_role_id):
            await calc_matcher.finish("全局玩家ID输入有误，请检查后重试！")
        if not is_specific_calculator:
            resolved_tag = await _resolve_bare_calculator_tag_for_global_role_id(
                int(global_role_id),
                state,
                selection_key="calculator_kungfu_options",
            )
            if resolved_tag == "":
                state["calculator_kungfu_context"] = {
                    "mode": "global",
                    "global_role_id": int(global_role_id),
                }
                await calc_matcher.send(_format_special_pve_kungfu_selection(state["calculator_kungfu_options"]))
                return
            tag = resolved_tag
        instance = await UniversalCalculator.with_global_role_id(int(global_role_id), tag)
        if isinstance(instance, str):
            await calc_matcher.finish(instance)
        instance = cast(UniversalCalculator, instance)
    else:
        server = Server(server, event.group_id).server
        if server is None:
            await calc_matcher.finish(PROMPT.ServerNotExist)
        if not is_specific_calculator:
            player_data = await search_player(role_name=name, server_name=server)
            if player_data.roleId == "":
                await calc_matcher.finish(PROMPT.PlayerNotExist)
            await JX3PlayerAttribute.from_tuilan(player_data.roleId, player_data.serverName, player_data.globalRoleId)
            resolved_tag = await _resolve_bare_calculator_tag_for_global_role_id(
                int(player_data.globalRoleId),
                state,
                selection_key="calculator_kungfu_options",
            )
            if resolved_tag == "":
                state["calculator_kungfu_context"] = {
                    "mode": "name",
                    "server": server,
                    "name": name,
                }
                await calc_matcher.send(_format_special_pve_kungfu_selection(state["calculator_kungfu_options"]))
                return
            tag = resolved_tag
        instance = await UniversalCalculator.with_name(name, server, tag)
        if isinstance(instance, str):
            await calc_matcher.finish(instance)
        instance = cast(UniversalCalculator, instance)
    await _prepare_calculator_loop_selection(event, matcher, state, instance)

@calc_matcher.got("loop_order")
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await calc_matcher.finish("循环选择有误，请重新发起命令！")
    if "calculator_kungfu_options" in state:
        options: list[dict[str, Any]] = state["calculator_kungfu_options"]
        index = int(num)
        if index < 1 or index > len(options):
            await calc_matcher.finish("超出可选范围，请重新发起命令！")
        selected_tag = str(options[index - 1]["tag"])
        context: dict[str, Any] = state["calculator_kungfu_context"]
        if context["mode"] == "global":
            candidate = await UniversalCalculator.with_global_role_id(int(context["global_role_id"]), selected_tag)
        else:
            candidate = await UniversalCalculator.with_name(str(context["name"]), str(context["server"]), selected_tag)
        if isinstance(candidate, str):
            await calc_matcher.finish(candidate)
        instance = cast(UniversalCalculator, candidate)
        state.pop("calculator_kungfu_options", None)
        state.pop("calculator_kungfu_context", None)
        state.pop("loop_order", None)
        await _prepare_calculator_loop_selection(event, matcher, state, instance)
        await calc_matcher.reject()
    loops: list[dict[str, Any]] = state["loops"]
    instance: UniversalCalculator | JX3BOXCalculator = state["instance"]
    index = int(num)
    if index < 1 or index > len(loops):
        await calc_matcher.finish("超出可选范围，请重新发起命令！")
    loop_entry = loops[index - 1]
    loop_code: dict[str, str] = {
        "weapon": str(loop_entry.get("weapon", "")),
        "haste": str(loop_entry.get("haste", "")),
        "loop": str(loop_entry.get("loop", "")),
    }
    data = await instance.image(loop_code, int(loop_entry.get("user_id") or 0))

    if state["pzid"] != 0:
        equip_image = ms.image(await get_equip_image(str(state["pzid"])))
        await calc_matcher.send(equip_image)
    await calc_matcher.finish(data)

equip_compare = on_command("jx3_equip_compare", aliases={"装备对比", "T装备对比", "QC装备对比", "JC装备对比", "TL装备对比", "JY装备对比", "WX装备对比"}, priority=5, force_whitespace=True)

@equip_compare.handle()
async def _(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    args: Message = CommandArg(),
    cmd: str = RawCommand(),
):
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
    else:
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
    tag = _calculator_tag_from_command(cmd)
    if not _calculator_command_has_specific_prefix(cmd):
        resolved_tag = await _resolve_bare_calculator_tag_for_global_role_id(
            int(player_data.globalRoleId),
            state,
            selection_key="equip_compare_kungfu_options",
        )
        if resolved_tag == "":
            state["equip_compare_kungfu_context"] = {
                "global_role_id": int(player_data.globalRoleId),
                "equip_name": equip,
            }
            await equip_compare.send(_format_special_pve_kungfu_selection(state["equip_compare_kungfu_options"]))
            return
        tag = resolved_tag
    instance = await JX3PlayerAttribute.from_database(int(player_data.globalRoleId), tag, False)
    if instance is None:
        await equip_compare.finish(PROMPT.EquipNotFound)
    await _prepare_equip_compare_equipment_selection(event, matcher, state, instance, equip)
    return

@equip_compare.got("equip_index")
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, equip_index: Message = Arg()):
    num = equip_index.extract_plain_text()
    if not check_number(num):
        await equip_compare.finish("装备选择有误，请重新发起命令！")
    if "equip_compare_kungfu_options" in state:
        options: list[dict[str, Any]] = state["equip_compare_kungfu_options"]
        index = int(num)
        if index < 1 or index > len(options):
            await equip_compare.finish("超出可选范围，请重新发起命令！")
        selected_tag = str(options[index - 1]["tag"])
        context: dict[str, Any] = state["equip_compare_kungfu_context"]
        instance = await JX3PlayerAttribute.from_database(int(context["global_role_id"]), selected_tag, False)
        if instance is None:
            await equip_compare.finish(PROMPT.EquipNotFound)
        state.pop("equip_compare_kungfu_options", None)
        state.pop("equip_compare_kungfu_context", None)
        state.pop("equip_index", None)
        await _prepare_equip_compare_equipment_selection(event, matcher, state, instance, str(context["equip_name"]))
        await equip_compare.reject()
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
    income_code = get_calculator_income_codes(income_ver, int(str(kungfu_id)))
    formation_code = FORMATIONS[formation_ver]

    new_dps_data.income_list = income_code
    new_dps_data.income_ver = income_ver
    new_dps_data.formation_list = formation_code
    new_dps_data.formation_name = formation_ver
    state["updated_data"] = new_dps_data

    is_custom = Preference(event.user_id, "", "").setting("计算器来源") == "自定义"
    loop_entries = await _calculator_loop_entries(new_dps_data, event.user_id, is_custom)
    if isinstance(loop_entries, str):
        await equip_compare.finish(loop_entries)
    state["loops"] = loop_entries
    await equip_compare.send(_format_calculator_loop_selection(loop_entries))
    return

@equip_compare.got("loop_order")
async def _(event: GroupMessageEvent, state: T_State, loop_order: Message = Arg()):
    num = loop_order.extract_plain_text()
    if not check_number(num):
        await equip_compare.finish("循环选择有误，请重新发起命令！")
    loops: list[dict[str, Any]] = state["loops"]
    index = int(num)
    if index < 1 or index > len(loops):
        await equip_compare.finish("超出可选范围，请重新发起命令！")
    loop_entry = loops[index - 1]
    loop_code: dict[str, str] = {
        "weapon": str(loop_entry.get("weapon", "")),
        "haste": str(loop_entry.get("haste", "")),
        "loop": str(loop_entry.get("loop", "")),
    }
    old_instance: UniversalCalculator = state["current_data"]
    new_instance: UniversalCalculator = state["updated_data"]
    loop_user_id = int(loop_entry.get("user_id") or 0)

    old_data = await old_instance.calculate(loop_code, loop_user_id)
    new_data = await new_instance.calculate(loop_code, loop_user_id)
    if not isinstance(old_data, dict) or not isinstance(new_data, dict):
        await equip_compare.finish(cast(str, old_data))
    old_dps = old_data['damage_per_second']
    new_dps = new_data['damage_per_second']
    margin = str(round((new_dps / old_dps - 1) * 100, 3)) + "%"
    msg = f"当前DPS：{old_dps}\n更新DPS：{new_dps}\n提升幅度：{margin}"
    if loop_user_id:
        msg += "\n提示：当前正在使用自定义循环！"
    await equip_compare.finish(msg)


PUBLIC_LOOP_SUBMIT_HELP_TEXT = (
    "提交公有循环参数：\n"
    "1. 发送「提交公有循环」列出你上传过的全部自定义循环\n"
    "2. 发送「提交公有循环 <心法名>」只列出指定心法的自定义循环\n"
    "3. 机器人返回列表后，发送要提交的编号；提交后会发送到审批群等待审批用户处理\n"
    "示例：\n"
    "提交公有循环 莫问\n"
    "循环列表返回后发送：1"
)

PUBLIC_LOOP_APPROVAL_HELP_TEXT = (
    "公有循环审批 help：\n"
    "【用户提交】\n"
    "1. 提交公有循环：列出你上传过的全部自定义循环\n"
    "2. 提交公有循环 <心法名>：只列出指定心法的自定义循环\n"
    "3. 返回列表后发送编号，提交到审批群等待处理\n"
    "4. 循环改名 <心法名>：变更你提供的公有循环和对应私有循环名字\n"
    f"5. 循环改名 <QQ号> <心法名>：拥有 {CALCULATOR_LOOP_RENAME_OTHER_PERMISSION_NODE} 权限时可变更指定用户提供的循环名字\n\n"
    "【审批处理】\n"
    "1. 公有循环审批：列出全部待审批循环，仅配置的审批群内可用\n"
    "2. 返回列表后发送编号，机器人会生成循环曲线预览\n"
    "3. 预览装备优先使用该心法专用配置，未配置则使用 JCL 内置装备\n"
    "4. 预览后发送 Y/是：通过审批并移动到公用循环库\n"
    "5. 预览后发送 N/否：驳回并移除待审标记，不删除用户私有 JCL\n"
    f"6. 拥有 {PUBLIC_LOOP_APPROVE_PERMISSION_NODE} 权限的用户可审批\n\n"
    f"【审批配置，需要 {PUBLIC_LOOP_CONFIG_PERMISSION_NODE} 权限】\n"
    "1. 公有循环审批设置：查看当前配置\n"
    "2. 公有循环审批设置 群 <群号>\n"
    "3. 公有循环审批设置 群 当前群\n"
    "4. 公有循环审批设置 装备 <心法名> JCL\n"
    "5. 公有循环审批设置 装备 <心法名> 玩家 <服务器> <角色名>\n"
    "6. 公有循环审批设置 装备 <心法名> 魔盒 <配装ID>\n"
    "7. 公有循环审批设置 装备 列表\n"
    "8. 公有循环审批设置 列表"
)

PUBLIC_LOOP_APPROVAL_CONFIG_HELP_TEXT = (
    "公有循环审批设置参数：\n"
    f"1. 需要 {PUBLIC_LOOP_CONFIG_PERMISSION_NODE} 权限\n"
    "2. 查看配置：公有循环审批设置\n"
    "3. 设置审批群：公有循环审批设置 群 <群号>\n"
    "4. 设置当前群为审批群：公有循环审批设置 群 当前群\n"
    f"5. 审批用户请授予 {PUBLIC_LOOP_APPROVE_PERMISSION_NODE} 权限\n"
    "6. 恢复指定心法默认装备：公有循环审批设置 装备 <心法名> JCL\n"
    "7. 设置指定心法预览装备：公有循环审批设置 装备 <心法名> 玩家 <服务器> <角色名>\n"
    "8. 设置指定心法预览装备：公有循环审批设置 装备 <心法名> 魔盒 <配装ID>\n"
    "9. 查看心法装备配置：公有循环审批设置 装备 列表\n"
    "10. 查看配置：公有循环审批设置 列表"
)


def _default_public_loop_approval_config() -> dict[str, Any]:
    return {
        "approval_group_id": PUBLIC_LOOP_DEFAULT_APPROVAL_GROUP_ID,
        "approver_user_ids": [],
        "preview_equipment_by_kungfu": {},
    }


def _normalize_public_loop_preview_equipment(preview: Any) -> dict[str, Any] | None:
    if not isinstance(preview, dict):
        return None
    source = str(preview.get("source") or "jcl").lower()
    if source == "player":
        server = str(preview.get("server") or "").strip()
        name = str(preview.get("name") or "").strip()
        if server and name:
            return {"source": "player", "server": server, "name": name}
        return None
    if source in {"jx3box", "box", "pzid"}:
        try:
            pzid = int(preview.get("pzid") or 0)
        except (TypeError, ValueError):
            pzid = 0
        if pzid > 0:
            return {"source": "jx3box", "pzid": pzid}
        return None
    if source == "jcl":
        return {"source": "jcl"}
    return None


def _normalize_public_loop_approval_config(data: Any) -> dict[str, Any]:
    config = _default_public_loop_approval_config()
    if not isinstance(data, dict):
        return config
    try:
        group_id = int(data.get("approval_group_id") or config["approval_group_id"])
    except (TypeError, ValueError):
        group_id = config["approval_group_id"]
    approvers = []
    for user_id in data.get("approver_user_ids") or []:
        try:
            parsed_id = int(user_id)
        except (TypeError, ValueError):
            continue
        if parsed_id not in approvers:
            approvers.append(parsed_id)
    config["approval_group_id"] = group_id
    config["approver_user_ids"] = approvers
    preview_by_kungfu: dict[str, dict[str, Any]] = {}
    raw_preview_by_kungfu = data.get("preview_equipment_by_kungfu") or {}
    if isinstance(raw_preview_by_kungfu, dict):
        for raw_kungfu_id, raw_preview in raw_preview_by_kungfu.items():
            try:
                kungfu_id = int(raw_kungfu_id)
            except (TypeError, ValueError):
                continue
            if kungfu_id <= 0:
                continue
            preview = _normalize_public_loop_preview_equipment(raw_preview)
            if preview is not None:
                preview_by_kungfu[str(kungfu_id)] = preview
    config["preview_equipment_by_kungfu"] = preview_by_kungfu
    return config


def _load_public_loop_approval_config() -> dict[str, Any]:
    raw_content = read(PUBLIC_LOOP_APPROVAL_CONFIG_PATH)
    if not raw_content:
        return _default_public_loop_approval_config()
    try:
        return _normalize_public_loop_approval_config(json.loads(raw_content))
    except json.JSONDecodeError:
        return _default_public_loop_approval_config()


def _save_public_loop_approval_config(config: dict[str, Any]) -> None:
    normalized = _normalize_public_loop_approval_config(config)
    write(PUBLIC_LOOP_APPROVAL_CONFIG_PATH, json.dumps(normalized, ensure_ascii=False, indent=2))


def _public_loop_approval_group_id() -> int:
    return int(_load_public_loop_approval_config()["approval_group_id"])


def _format_public_loop_preview_equipment(preview: dict[str, Any]) -> str:
    source = preview.get("source")
    if source == "player":
        return f"玩家装备：{preview.get('server')} {preview.get('name')}"
    if source == "jx3box":
        return f"魔盒配装：{preview.get('pzid')}"
    return "JCL 内置装备"


def _format_public_loop_preview_equipment_config(config: dict[str, Any]) -> str:
    preview_by_kungfu = config.get("preview_equipment_by_kungfu") or {}
    if not isinstance(preview_by_kungfu, dict) or not preview_by_kungfu:
        return "预览装备：未配置心法专用装备，未配置时默认使用 JCL 内置装备。"
    lines = ["预览装备："]
    for kungfu_id in sorted(preview_by_kungfu, key=lambda value: int(value) if str(value).isdigit() else 0):
        preview = preview_by_kungfu.get(kungfu_id)
        if not isinstance(preview, dict):
            continue
        lines.append(
            f"{_public_loop_kungfu_name(kungfu_id)}（{kungfu_id}）："
            f"{_format_public_loop_preview_equipment(preview)}"
        )
    lines.append("未配置的心法默认使用 JCL 内置装备。")
    return "\n".join(lines)


def _public_loop_preview_equipment_for_kungfu(kungfu_id: int) -> dict[str, Any]:
    config = _load_public_loop_approval_config()
    preview_by_kungfu = config["preview_equipment_by_kungfu"]
    preview = preview_by_kungfu.get(str(kungfu_id))
    if isinstance(preview, dict):
        return preview
    return {"source": "jcl"}


def _parse_public_loop_config_kungfu_id(value: str) -> int | None:
    if _is_positive_integer_text(value):
        return int(value)
    kungfu = Kungfu(value)
    if kungfu.id is None:
        return None
    return int(kungfu.id)


def _format_public_loop_approval_config() -> str:
    config = _load_public_loop_approval_config()
    return (
        "当前公有循环审批配置：\n"
        f"审批群：{config['approval_group_id']}\n"
        f"审批权限节点：{PUBLIC_LOOP_APPROVE_PERMISSION_NODE}\n"
        f"配置权限节点：{PUBLIC_LOOP_CONFIG_PERMISSION_NODE}\n"
        f"{_format_public_loop_preview_equipment_config(config)}\n"
        "审批用户请通过权限节点授予，不再使用单独的审批用户列表。"
    )


def _public_loop_preview_tag(kungfu_id: int) -> str:
    special_tags = {
        10014: "QCPVE",
        10015: "JCPVE",
        10224: "JYPVE",
        10225: "TLPVE",
        10821: "WXPVE",
    }
    if kungfu_id in special_tags:
        return special_tags[kungfu_id]
    kungfu = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True)
    if kungfu.abbr == "T":
        return "TPVE"
    return "DPSPVE"


def _apply_public_loop_preview_environment(instance: UniversalCalculator | JX3BOXCalculator) -> None:
    instance.income_list = []
    instance.income_ver = "无增益"
    instance.formation_list = []
    instance.formation_name = "无阵眼"


async def _public_loop_preview_instance(
    event: GroupMessageEvent,
    kungfu_id: int,
) -> tuple[UniversalCalculator | JX3BOXCalculator, list[list] | None, str] | str:
    preview = _public_loop_preview_equipment_for_kungfu(kungfu_id)
    source = preview.get("source")
    if source == "jx3box":
        pzid = int(preview.get("pzid") or 0)
        instance = await JX3BOXCalculator.with_pzid(pzid)
        if isinstance(instance, str):
            return f"审批预览装备获取失败：{instance}"
        instance.info = ("待审循环", f"魔盒配装 {pzid}")
        _apply_public_loop_preview_environment(instance)
        return instance, normalize_calculator_jcl_data(instance.jcl_data), f"魔盒配装 {pzid}"

    if source == "player":
        server = Server(str(preview.get("server") or ""), event.group_id).server
        name = str(preview.get("name") or "").strip()
        if server is None or not name:
            return "审批预览装备配置有误，请重新设置玩家装备。"
        instance = await UniversalCalculator.with_name(name, server, _public_loop_preview_tag(kungfu_id))
        if isinstance(instance, str):
            return f"审批预览装备获取失败：{instance}"
        jcl_data = instance.jcl_data if getattr(instance, "jcl_data", None) else instance.equip_data.equip_lines
        _apply_public_loop_preview_environment(instance)
        return instance, normalize_calculator_jcl_data(jcl_data), f"{server} {name}"

    instance = UniversalCalculator(jcl_data=[], kungfu_id=kungfu_id, info=("待审循环", "JCL内置装备"))
    _apply_public_loop_preview_environment(instance)
    return instance, None, "JCL内置装备"


async def _request_public_loop_preview(
    submission: dict[str, Any],
    jcl_data: list[list] | None,
) -> dict[str, Any] | str:
    payload: dict[str, Any] = {
        "submission_id": int(submission.get("id") or 0),
        "full_income": [],
        "bin_size": DEFAULT_DAMAGE_TIMELINE_BIN_SIZE,
        "rolling_window": DEFAULT_DAMAGE_TIMELINE_ROLLING_WINDOW,
    }
    if jcl_data is not None:
        payload["jcl_data"] = jcl_data
    try:
        result = (
            await Request(
                f"{Config.jx3.api.calculator_url}/preview_public_loop",
                params=payload,
            ).post(timeout=120)
        ).json()
    except Exception as exc:
        return f"公有循环审批预览失败：{exc}"
    if result.get("code") != 200:
        return str(result.get("msg") or "公有循环审批预览失败。")
    return result["data"]


def _public_loop_kungfu_name(kungfu_id: Any) -> str:
    try:
        kungfu = Kungfu.with_internel_id(int(kungfu_id), convert_to_pc=True)
    except (TypeError, ValueError):
        return "未知心法"
    return kungfu.name or str(kungfu_id)


def _format_public_loop_time(value: Any) -> str:
    return str(value or "未知时间")


def _is_positive_integer_text(value: str) -> bool:
    return value.isdigit() and int(value) > 0


async def _fetch_custom_loops_for_public_submission(user_id: int, kungfu_id: int = 0) -> list[dict[str, Any]] | str:
    params: dict[str, int] = {"user_id": user_id}
    if kungfu_id:
        params["kungfu_id"] = kungfu_id
    try:
        result = (
            await Request(
                f"{Config.jx3.api.calculator_url}/custom_loops",
                params=params,
            ).get()
        ).json()
    except Exception:
        return "循环列表获取失败，请确认 calculator 服务可用后重试！"
    loops = result.get("data") or []
    if result.get("code") != 200 or not isinstance(loops, list):
        return []
    return loops


def _format_submit_public_loop_selection(loops: list[dict[str, Any]]) -> str:
    msg = "请选择要提交为公有循环的自定义循环：\n发送「取消」可取消。"
    for index, loop in enumerate(loops, start=1):
        kungfu_name = _public_loop_kungfu_name(loop.get("kungfu_id"))
        status = "（已提交待审）" if loop.get("submitted") else ""
        file_name = loop.get("file") or loop.get("name") or "未命名循环"
        msg += f"\n{index}. [{kungfu_name}] {file_name}{status}"
    return msg


async def _send_public_loop_approval_notice(
    bot: Bot,
    submitter_id: int,
    loop_record: dict[str, Any],
) -> str | None:
    kungfu_name = _public_loop_kungfu_name(loop_record.get("kungfu_id"))
    file_name = loop_record.get("file") or loop_record.get("name") or "未命名循环"
    submitted_at = _format_public_loop_time(loop_record.get("submitted_at"))
    message = (
        "公有循环提交待审批：\n"
        f"用户 {submitter_id} 上传了 {file_name} 循环\n"
        f"心法：{kungfu_name}\n"
        f"提交时间：{submitted_at}\n"
        "有审批权限的用户发送「公有循环审批」可发起审批。"
    )
    try:
        await bot.send_group_msg(group_id=_public_loop_approval_group_id(), message=message)
    except Exception as exc:
        return str(exc)
    return None


def _format_public_loop_submissions(submissions: list[dict[str, Any]]) -> str:
    msg = "待审批公有循环：\n发送序号通过审批；发送「取消」可取消。"
    for index, item in enumerate(submissions, start=1):
        kungfu_name = _public_loop_kungfu_name(item.get("kungfu_id"))
        file_name = item.get("file") or item.get("name") or "未命名循环"
        submitted_at = _format_public_loop_time(item.get("submitted_at"))
        exists_text = "" if item.get("exists", True) else "（源文件缺失）"
        msg += (
            f"\n{index}. {file_name}{exists_text}"
            f"\n   心法：{kungfu_name}｜提交用户：{item.get('user_id', '未知')}｜提交时间：{submitted_at}"
        )
    return msg


async def _ensure_public_loop_approval_permission(event: GroupMessageEvent, matcher: Matcher) -> None:
    approval_group_id = _public_loop_approval_group_id()
    if event.group_id != approval_group_id:
        await matcher.finish(f"公有循环审批只能在配置的审批群 {approval_group_id} 使用。")
    if not check_permission(event.user_id, PUBLIC_LOOP_APPROVE_PERMISSION_NODE):
        await matcher.finish(denied(PUBLIC_LOOP_APPROVE_PERMISSION_NODE))


submit_public_loop_matcher = on_command("jx3_submit_public_loop", aliases={"提交公有循环"}, priority=5, force_whitespace=True)


@submit_public_loop_matcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    query = args.extract_plain_text().strip()
    if query.lower() in {"help", "帮助", "参数", "示例"}:
        await submit_public_loop_matcher.finish(PUBLIC_LOOP_SUBMIT_HELP_TEXT)
    kungfu_id = 0
    if query:
        kungfu = Kungfu(query)
        if kungfu.id is None:
            await submit_public_loop_matcher.finish("心法输入有误，请检查后重试！")
        kungfu_id = kungfu.id
    loops = await _fetch_custom_loops_for_public_submission(event.user_id, kungfu_id)
    if isinstance(loops, str):
        await submit_public_loop_matcher.finish(loops)
    if not loops:
        await submit_public_loop_matcher.finish("未找到你上传的自定义循环。")
    state["submit_public_loop_items"] = loops
    await submit_public_loop_matcher.send(_format_submit_public_loop_selection(loops))


@submit_public_loop_matcher.got("public_loop_order")
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, public_loop_order: Message = Arg()):
    text = public_loop_order.extract_plain_text().strip()
    if text in {"取消", "cancel", "Cancel", "CANCEL"}:
        await submit_public_loop_matcher.finish("已取消提交公有循环。")
    if not _is_positive_integer_text(text):
        await submit_public_loop_matcher.finish("循环选择有误，请重新发起命令！")
    loops: list[dict[str, Any]] = state.get("submit_public_loop_items") or []
    index = int(text)
    if not loops or index < 1 or index > len(loops):
        await submit_public_loop_matcher.finish("超出可选范围，请重新发起命令！")
    loop = loops[index - 1]
    payload = {
        "user_id": event.user_id,
        "kungfu_id": int(loop.get("kungfu_id") or 0),
        "file_name": str(loop.get("file") or ""),
    }
    try:
        result = (
            await Request(
                f"{Config.jx3.api.calculator_url}/submit_public_loop",
                params=payload,
            ).post()
        ).json()
    except Exception:
        await submit_public_loop_matcher.finish("提交失败，请确认 calculator 服务可用后重试！")
    if result.get("code") != 200:
        await submit_public_loop_matcher.finish("提交失败：" + str(result.get("msg", "")))
    loop_record = result.get("data") or {}
    msg = str(result.get("msg") or "循环已提交公有审批。")
    already_pending = "已在待审批列表" in msg
    notify_error = None
    if not already_pending:
        notify_error = await _send_public_loop_approval_notice(bot, event.user_id, loop_record)
    if already_pending:
        msg += "\n无需重复通知审批群。"
    elif notify_error:
        msg += f"\n但审批群消息发送失败：{notify_error}"
    else:
        msg += "\n已通知审批群，请等待审批用户处理。"
    await submit_public_loop_matcher.finish(msg)


public_loop_approval_config_matcher = on_command("jx3_public_loop_approval_config", aliases={"公有循环审批设置", "公有循环审批配置"}, priority=5, force_whitespace=True)


@public_loop_approval_config_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if not check_permission(event.user_id, PUBLIC_LOOP_CONFIG_PERMISSION_NODE):
        await public_loop_approval_config_matcher.finish(denied(PUBLIC_LOOP_CONFIG_PERMISSION_NODE))
    raw_text = args.extract_plain_text().strip()
    if raw_text == "":
        await public_loop_approval_config_matcher.finish(_format_public_loop_approval_config())
    if raw_text.lower() in {"help", "帮助", "参数", "示例"}:
        await public_loop_approval_config_matcher.finish(PUBLIC_LOOP_APPROVAL_CONFIG_HELP_TEXT)

    parts = [part for part in raw_text.split() if part]
    command = parts[0] if parts else ""
    config = _load_public_loop_approval_config()

    if command in {"列表", "查看", "配置"}:
        await public_loop_approval_config_matcher.finish(_format_public_loop_approval_config())

    if command in {"群", "审批群", "设置群"}:
        if len(parts) != 2:
            await public_loop_approval_config_matcher.finish("参考格式：公有循环审批设置 群 <群号>\n也可以使用：公有循环审批设置 群 当前群")
        group_arg = parts[1]
        if group_arg in {"当前群", "本群", "当前"}:
            group_id = int(event.group_id)
        elif _is_positive_integer_text(group_arg):
            group_id = int(group_arg)
        else:
            await public_loop_approval_config_matcher.finish("审批群号输入有误，请检查后重试。")
        config["approval_group_id"] = group_id
        _save_public_loop_approval_config(config)
        await public_loop_approval_config_matcher.finish(f"已设置公有循环审批群：{group_id}")

    if command in {"添加", "新增", "授权"}:
        await public_loop_approval_config_matcher.finish(
            "公有循环审批用户已改用权限节点管理。\n"
            f"请授予用户 {PUBLIC_LOOP_APPROVE_PERMISSION_NODE} 权限。"
        )

    if command in {"删除", "移除", "取消授权"}:
        await public_loop_approval_config_matcher.finish(
            "公有循环审批用户已改用权限节点管理。\n"
            f"请移除用户 {PUBLIC_LOOP_APPROVE_PERMISSION_NODE} 权限。"
        )

    if command in {"装备", "预览装备"}:
        equipment_help_text = (
            "参考格式：公有循环审批设置 装备 <心法名> JCL\n"
            "参考格式：公有循环审批设置 装备 <心法名> 玩家 <服务器> <角色名>\n"
            "参考格式：公有循环审批设置 装备 <心法名> 魔盒 <配装ID>\n"
            "查看心法装备配置：公有循环审批设置 装备 列表"
        )
        if len(parts) < 2:
            await public_loop_approval_config_matcher.finish(
                equipment_help_text
            )
        if parts[1] in {"列表", "查看", "配置"}:
            await public_loop_approval_config_matcher.finish(
                _format_public_loop_preview_equipment_config(config)
            )
        if len(parts) < 3:
            await public_loop_approval_config_matcher.finish("请先指定心法。\n" + equipment_help_text)
        kungfu_id = _parse_public_loop_config_kungfu_id(parts[1])
        if kungfu_id is None:
            await public_loop_approval_config_matcher.finish("心法输入有误，请检查后重试。")
        kungfu_name = _public_loop_kungfu_name(kungfu_id)
        preview_by_kungfu = dict(config.get("preview_equipment_by_kungfu") or {})
        source_arg = parts[2].lower()
        if source_arg == "jcl":
            preview_by_kungfu.pop(str(kungfu_id), None)
            config["preview_equipment_by_kungfu"] = preview_by_kungfu
            _save_public_loop_approval_config(config)
            await public_loop_approval_config_matcher.finish(
                f"已恢复 {kungfu_name} 审批预览装备：JCL 内置装备"
            )
        if parts[2] == "玩家":
            if len(parts) != 5:
                await public_loop_approval_config_matcher.finish(
                    "参考格式：公有循环审批设置 装备 <心法名> 玩家 <服务器> <角色名>"
                )
            preview_by_kungfu[str(kungfu_id)] = {
                "source": "player",
                "server": parts[3],
                "name": parts[4],
            }
            config["preview_equipment_by_kungfu"] = preview_by_kungfu
            _save_public_loop_approval_config(config)
            await public_loop_approval_config_matcher.finish(
                f"已设置 {kungfu_name} 审批预览装备：玩家 {parts[3]} {parts[4]}"
            )
        if parts[2] == "魔盒":
            if len(parts) != 4 or not _is_positive_integer_text(parts[3]):
                await public_loop_approval_config_matcher.finish(
                    "参考格式：公有循环审批设置 装备 <心法名> 魔盒 <配装ID>"
                )
            pzid = int(parts[3])
            preview_by_kungfu[str(kungfu_id)] = {"source": "jx3box", "pzid": pzid}
            config["preview_equipment_by_kungfu"] = preview_by_kungfu
            _save_public_loop_approval_config(config)
            await public_loop_approval_config_matcher.finish(
                f"已设置 {kungfu_name} 审批预览装备：魔盒配装 {pzid}"
            )
        await public_loop_approval_config_matcher.finish(PUBLIC_LOOP_APPROVAL_CONFIG_HELP_TEXT)

    await public_loop_approval_config_matcher.finish(PUBLIC_LOOP_APPROVAL_CONFIG_HELP_TEXT)


approve_public_loop_matcher = on_command("jx3_approve_public_loop", aliases={"公有循环审批", "审批公有循环"}, priority=5, force_whitespace=True)


@approve_public_loop_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg()):
    await _ensure_public_loop_approval_permission(event, matcher)
    query = args.extract_plain_text().strip()
    if query.lower() in {"help", "帮助", "参数", "示例"}:
        await approve_public_loop_matcher.finish(PUBLIC_LOOP_APPROVAL_HELP_TEXT)
    if query:
        await approve_public_loop_matcher.finish("参考格式：公有循环审批")
    try:
        result = (await Request(f"{Config.jx3.api.calculator_url}/public_loop_submissions").get()).json()
    except Exception:
        await approve_public_loop_matcher.finish("待审批列表获取失败，请确认 calculator 服务可用后重试！")
    submissions = result.get("data") or []
    if result.get("code") != 200 or not isinstance(submissions, list) or not submissions:
        await approve_public_loop_matcher.finish("当前没有待审批公有循环。")
    state["public_loop_submissions"] = submissions
    await approve_public_loop_matcher.send(_format_public_loop_submissions(submissions))


@approve_public_loop_matcher.got("public_loop_approval_order")
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, public_loop_approval_order: Message = Arg()):
    await _ensure_public_loop_approval_permission(event, matcher)
    text = public_loop_approval_order.extract_plain_text().strip()
    if text in {"取消", "cancel", "Cancel", "CANCEL"}:
        await approve_public_loop_matcher.finish("已取消公有循环审批。")
    if not _is_positive_integer_text(text):
        await approve_public_loop_matcher.finish("审批序号有误，请重新发起命令！")
    submissions: list[dict[str, Any]] = state.get("public_loop_submissions") or []
    index = int(text)
    if not submissions or index < 1 or index > len(submissions):
        await approve_public_loop_matcher.finish("超出可选范围，请重新发起命令！")
    selected = submissions[index - 1]
    kungfu_id = int(selected.get("kungfu_id") or 0)
    preview_instance = await _public_loop_preview_instance(event, kungfu_id)
    if isinstance(preview_instance, str):
        await approve_public_loop_matcher.finish(preview_instance)
    instance, jcl_data, equipment_source = preview_instance
    await approve_public_loop_matcher.send("正在生成待审循环曲线预览。")
    preview_data = await _request_public_loop_preview(selected, jcl_data)
    if isinstance(preview_data, str):
        await approve_public_loop_matcher.finish(preview_data)
    state["public_loop_selected_submission"] = selected
    state["public_loop_preview_equipment_source"] = equipment_source
    await approve_public_loop_matcher.send(await _render_damage_timeline_image(preview_data, instance, compare=False))
    await approve_public_loop_matcher.send(
        "是否通过该公有循环审批？\n"
        f"预览装备：{equipment_source}\n"
        "发送 Y 通过并移动到公用循环库；发送 N 驳回并移除待审标记。"
    )


@approve_public_loop_matcher.got("public_loop_approval_confirm")
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, public_loop_approval_confirm: Message = Arg()):
    await _ensure_public_loop_approval_permission(event, matcher)
    selected: dict[str, Any] = state.get("public_loop_selected_submission") or {}
    if not selected:
        await approve_public_loop_matcher.finish("公有循环审批状态已失效，请重新发起命令。")
    text = public_loop_approval_confirm.extract_plain_text().strip().lower()
    if text not in {"y", "yes", "是", "n", "no", "否"}:
        await approve_public_loop_matcher.finish("审批确认输入有误，请重新发起命令。")
    api_path = "approve_public_loop" if text in {"y", "yes", "是"} else "reject_public_loop"
    payload = {
        "submission_id": int(selected.get("id") or 0),
        "approver_id": event.user_id,
    }
    try:
        result = (
            await Request(
                f"{Config.jx3.api.calculator_url}/{api_path}",
                params=payload,
            ).post()
        ).json()
    except Exception:
        await approve_public_loop_matcher.finish("审批失败，请确认 calculator 服务可用后重试！")
    if result.get("code") != 200:
        await approve_public_loop_matcher.finish("审批失败：" + str(result.get("msg", "")))
    data = result.get("data") or {}
    kungfu_name = _public_loop_kungfu_name(data.get("kungfu_id"))
    if api_path == "reject_public_loop":
        await approve_public_loop_matcher.finish(
            "已驳回公有循环提交：\n"
            f"心法：{kungfu_name}\n"
            f"提交用户：{data.get('user_id', '未知')}\n"
            f"循环文件：{data.get('file') or '未知文件'}\n"
            "已移除待审标记，源自定义循环文件不会删除。"
        )
    await approve_public_loop_matcher.finish(
        "已通过公有循环审批：\n"
        f"心法：{kungfu_name}\n"
        f"提交用户：{data.get('user_id', '未知')}\n"
        f"公有循环文件：{data.get('public_file') or data.get('file') or '未知文件'}"
    )


RENAME_LOOP_HELP_TEXT = (
    "循环改名参数：\n"
    "1. 变更自己的循环：循环改名 <心法名>\n"
    f"2. 拥有 {CALCULATOR_LOOP_RENAME_OTHER_PERMISSION_NODE} 权限时可变更指定用户循环：循环改名 <QQ号> <心法名>\n"
    "3. 机器人返回列表后，发送要变更的编号，再发送新的循环名\n"
    "4. 只会变更该用户提供的公有循环，以及对应的用户私有循环\n"
    "示例：\n"
    "循环改名 莫问\n"
    "循环列表返回后发送：1\n"
    "然后发送：新循环名"
)


def _rename_loop_location_text(locations: list[str]) -> str:
    labels = {
        "public": "公有库",
        "private": "私有库",
    }
    return "、".join(labels.get(location, location) for location in locations) or "未知位置"


def _format_rename_loop_selection(target_user_id: int, kungfu_name: str, loops: list[dict[str, Any]]) -> str:
    msg = (
        f"请选择要变更名字的循环：{kungfu_name}\n"
        f"目标用户：{target_user_id}\n"
        "发送「取消」可取消。"
    )
    for index, loop in enumerate(loops, start=1):
        locations = _rename_loop_location_text(loop.get("locations") or [])
        file_parts = []
        if loop.get("public_file"):
            file_parts.append(f"公有：{loop['public_file']}")
        if loop.get("private_file"):
            file_parts.append(f"私有：{loop['private_file']}")
        file_text = "；".join(file_parts) if file_parts else str(loop.get("file") or "未知文件")
        msg += (
            f"\n{index}. {loop.get('name') or '未命名循环'}"
            f"\n   位置：{locations}"
            f"\n   文件：{file_text}"
        )
    return msg


def _safe_rename_loop_name(loop_name: str) -> str:
    safe_name = str(loop_name or "").strip()
    if (
        not safe_name
        or safe_name in {".", ".."}
        or safe_name.endswith(".jcl")
        or any(char in safe_name for char in '<>:"/\\|?*[]\r\n\t')
    ):
        return ""
    return safe_name


async def _fetch_renameable_loops(
    operator_id: int,
    target_user_id: int,
    kungfu_id: int,
    operator_can_rename_other: bool,
) -> list[dict[str, Any]] | str:
    try:
        result = (
            await Request(
                f"{Config.jx3.api.calculator_url}/renameable_loops",
                params={
                    "operator_id": operator_id,
                    "target_user_id": target_user_id,
                    "kungfu_id": kungfu_id,
                    "operator_is_owner": operator_can_rename_other,
                },
            ).get()
        ).json()
    except Exception:
        return "循环列表获取失败，请确认 calculator 服务可用后重试！"
    loops = result.get("data") or []
    if result.get("code") != 200:
        return str(result.get("msg") or "循环列表获取失败。")
    if not isinstance(loops, list):
        return []
    return loops


DELETE_LOOP_HELP_TEXT = (
    "删除循环参数：\n"
    "1. 只删除你自己上传的自定义循环，不会删除公用循环库\n"
    "2. 参考格式：删除循环 <心法名>\n"
    "3. 机器人返回循环列表后，发送要删除的编号，支持空格、半角逗号、全角逗号\n"
    "4. 删除该心法全部自定义循环：删除循环all <心法名>\n"
    "示例：\n"
    "删除循环 莫问\n"
    "循环列表返回后发送：1 或 1,2\n"
    "删除循环all 莫问"
)


def _format_delete_loop_selection(kungfu_name: str, loops: list[dict[str, Any]]) -> str:
    msg = (
        f"请选择要删除的自定义循环：{kungfu_name}\n"
        "支持空格、半角逗号、全角逗号；发送「取消」可取消。"
    )
    for index, loop in enumerate(loops, start=1):
        msg += f"\n{index}. {loop.get('name') or '未命名循环'}"
    return msg


def _parse_delete_loop_selection(text: str, loop_count: int) -> list[int] | str:
    parts = [part for part in re.split(r"[\s,，]+", text.strip()) if part]
    if not parts:
        return "请选择要删除的循环编号，请重新发起命令！"
    results: list[int] = []
    for part in parts:
        if not check_number(part):
            return "循环选择有误，请重新发起命令！"
        index = int(part)
        if index < 1 or index > loop_count:
            return "超出可选范围，请重新发起命令！"
        if index not in results:
            results.append(index)
    return results


rename_calculator_loop_matcher = on_command("jx3_rename_calc_loop", aliases={"循环改名", "改循环名", "修改循环名", "变更循环名字"}, priority=5, force_whitespace=True)


@rename_calculator_loop_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    query = args.extract_plain_text().strip()
    if query == "" or query.lower() in {"help", "帮助", "参数", "示例"}:
        await rename_calculator_loop_matcher.finish(RENAME_LOOP_HELP_TEXT)
    parts = [part for part in query.split() if part]
    operator_can_rename_other = check_permission(event.user_id, CALCULATOR_LOOP_RENAME_OTHER_PERMISSION_NODE)
    target_user_id = int(event.user_id)
    if len(parts) == 1:
        kungfu_arg = parts[0]
    elif len(parts) == 2 and _is_positive_integer_text(parts[0]):
        target_user_id = int(parts[0])
        if target_user_id != int(event.user_id) and not operator_can_rename_other:
            await rename_calculator_loop_matcher.finish(denied(CALCULATOR_LOOP_RENAME_OTHER_PERMISSION_NODE))
        kungfu_arg = parts[1]
    else:
        await rename_calculator_loop_matcher.finish(RENAME_LOOP_HELP_TEXT)

    kungfu_id = _parse_public_loop_config_kungfu_id(kungfu_arg)
    if kungfu_id is None:
        await rename_calculator_loop_matcher.finish("心法输入有误，请检查后重试！")
    loops = await _fetch_renameable_loops(
        int(event.user_id),
        target_user_id,
        kungfu_id,
        operator_can_rename_other,
    )
    if isinstance(loops, str):
        await rename_calculator_loop_matcher.finish(loops)
    if not loops:
        await rename_calculator_loop_matcher.finish("未找到该用户提供的可变更名字循环。")
    state["rename_loop_items"] = loops
    state["rename_loop_target_user_id"] = target_user_id
    state["rename_loop_kungfu_id"] = kungfu_id
    state["rename_loop_operator_can_rename_other"] = operator_can_rename_other
    await rename_calculator_loop_matcher.send(
        _format_rename_loop_selection(target_user_id, _public_loop_kungfu_name(kungfu_id), loops)
    )


@rename_calculator_loop_matcher.got("rename_loop_order")
async def _(state: T_State, rename_loop_order: Message = Arg()):
    text = rename_loop_order.extract_plain_text().strip()
    if text in {"取消", "cancel", "Cancel", "CANCEL"}:
        await rename_calculator_loop_matcher.finish("已取消循环改名。")
    if not _is_positive_integer_text(text):
        await rename_calculator_loop_matcher.finish("循环选择有误，请重新发起命令！")
    loops: list[dict[str, Any]] = state.get("rename_loop_items") or []
    index = int(text)
    if not loops or index < 1 or index > len(loops):
        await rename_calculator_loop_matcher.finish("超出可选范围，请重新发起命令！")
    selected = loops[index - 1]
    state["rename_loop_selected"] = selected
    await rename_calculator_loop_matcher.send(
        "请发送新的循环名。\n"
        "只需要发送循环名本身，不要带 .jcl，不要带心法、武器、加速前缀。\n"
        f"当前循环：{selected.get('name') or '未命名循环'}"
    )


@rename_calculator_loop_matcher.got("rename_loop_new_name")
async def _(event: GroupMessageEvent, state: T_State, rename_loop_new_name: Message = Arg()):
    raw_name = rename_loop_new_name.extract_plain_text()
    if raw_name.strip() in {"取消", "cancel", "Cancel", "CANCEL"}:
        await rename_calculator_loop_matcher.finish("已取消循环改名。")
    new_loop_name = _safe_rename_loop_name(raw_name)
    if not new_loop_name:
        await rename_calculator_loop_matcher.finish("新循环名无效，请不要使用路径符号、方括号、.jcl 后缀或空白名称。")
    selected: dict[str, Any] = state.get("rename_loop_selected") or {}
    target_user_id = int(state.get("rename_loop_target_user_id") or 0)
    kungfu_id = int(state.get("rename_loop_kungfu_id") or 0)
    if not selected or not target_user_id or not kungfu_id:
        await rename_calculator_loop_matcher.finish("循环改名状态已失效，请重新发起命令。")
    payload = {
        "operator_id": int(event.user_id),
        "target_user_id": target_user_id,
        "kungfu_id": kungfu_id,
        "file_name": str(selected.get("file") or selected.get("public_file") or selected.get("private_file") or ""),
        "new_loop_name": new_loop_name,
        "operator_is_owner": bool(state.get("rename_loop_operator_can_rename_other")),
    }
    try:
        result = (
            await Request(
                f"{Config.jx3.api.calculator_url}/rename_loop",
                params=payload,
            ).post()
        ).json()
    except Exception:
        await rename_calculator_loop_matcher.finish("循环改名失败，请确认 calculator 服务可用后重试！")
    if result.get("code") != 200:
        await rename_calculator_loop_matcher.finish("循环改名失败：" + str(result.get("msg", "")))
    data = result.get("data") or {}
    changes = data.get("changes") or []
    msg = (
        "循环名字变更成功：\n"
        f"目标用户：{target_user_id}\n"
        f"心法：{_public_loop_kungfu_name(kungfu_id)}\n"
        f"新循环名：{new_loop_name}"
    )
    for change in changes:
        msg += (
            f"\n{_rename_loop_location_text([str(change.get('location') or '')])}："
            f"{change.get('old_file') or '未知文件'} -> {change.get('new_file') or '未知文件'}"
        )
    if data.get("records_updated"):
        msg += "\n已同步更新公有循环审批记录。"
    await rename_calculator_loop_matcher.finish(msg)


remove_calculator_loop_matcher = on_command("jx3_rm_calc_loop", aliases={"删除循环"}, priority=5, force_whitespace=True)


@remove_calculator_loop_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    query = args.extract_plain_text().strip()
    if query == "" or query.lower() in {"help", "帮助", "参数", "示例"}:
        await remove_calculator_loop_matcher.finish(DELETE_LOOP_HELP_TEXT)
    if query.lower() == "all":
        await remove_calculator_loop_matcher.finish("删除循环不再支持 all，请使用「删除循环 <心法名>」后按列表选择要删除的循环。")

    kungfu = Kungfu(query)
    kungfu_id = kungfu.id
    if kungfu_id is None:
        await remove_calculator_loop_matcher.finish("心法输入有误，请检查后重试！")
    try:
        result = (
            await Request(
                f"{Config.jx3.api.calculator_url}/custom_loops",
                params={"kungfu_id": kungfu_id, "user_id": event.user_id},
            ).get()
        ).json()
    except Exception:
        await remove_calculator_loop_matcher.finish("循环列表获取失败，请确认 calculator 服务可用后重试！")
    loops = result.get("data") or []
    if result.get("code") != 200 or not isinstance(loops, list) or not loops:
        await remove_calculator_loop_matcher.finish("未找到你上传的该心法自定义循环。")
    state["delete_loop_kungfu_id"] = kungfu_id
    state["delete_loop_kungfu_name"] = kungfu.name or query
    state["delete_loop_items"] = loops
    await remove_calculator_loop_matcher.send(_format_delete_loop_selection(kungfu.name or query, loops))

@remove_calculator_loop_matcher.got("delete_loop_order")
async def _(event: GroupMessageEvent, state: T_State, delete_loop_order: Message = Arg()):
    text = delete_loop_order.extract_plain_text().strip()
    if text in {"取消", "cancel", "Cancel", "CANCEL"}:
        await remove_calculator_loop_matcher.finish("已取消删除循环。")
    loops: list[dict[str, Any]] = state.get("delete_loop_items") or []
    kungfu_id = int(state.get("delete_loop_kungfu_id") or 0)
    if not loops or kungfu_id == 0:
        await remove_calculator_loop_matcher.finish("删除循环状态已失效，请重新发起命令！")
    selected_indices = _parse_delete_loop_selection(text, len(loops))
    if isinstance(selected_indices, str):
        await remove_calculator_loop_matcher.finish(selected_indices)

    success = []
    failed = []
    for index in selected_indices:
        loop = loops[index - 1]
        params = {
            "user_id": event.user_id,
            "kungfu_id": kungfu_id,
            "loop_name": loop.get("name", ""),
        }
        if loop.get("file"):
            params["file_name"] = loop["file"]
        try:
            result = (await Request(f"{Config.jx3.api.calculator_url}/delete_loop", params=params).get()).json()
        except Exception as exc:
            failed.append(f"{index}. {loop.get('name') or '未命名循环'}：{exc}")
            continue
        if result.get("code") == 200:
            success.append(f"{index}. {loop.get('name') or '未命名循环'}")
        else:
            failed.append(f"{index}. {loop.get('name') or '未命名循环'}：{result.get('msg', '删除失败')}")
    msg = ""
    if success:
        msg += "已删除循环：\n" + "\n".join(success)
    if failed:
        if msg:
            msg += "\n"
        msg += "删除失败：\n" + "\n".join(failed)
    await remove_calculator_loop_matcher.finish(msg or "未删除任何循环。")


remove_all_calculator_loop_matcher = on_command("jx3_rm_all_calc_loop", aliases={"删除循环all"}, priority=5, force_whitespace=True)


@remove_all_calculator_loop_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    query = args.extract_plain_text().strip()
    if query == "" or query.lower() in {"help", "帮助", "参数", "示例"}:
        await remove_all_calculator_loop_matcher.finish("参考格式：删除循环all <心法名>\n示例：删除循环all 莫问")
    kungfu = Kungfu(query)
    kungfu_id = kungfu.id
    if kungfu_id is None:
        await remove_all_calculator_loop_matcher.finish("心法输入有误，请检查后重试！")
    try:
        result = (
            await Request(
                f"{Config.jx3.api.calculator_url}/delete_loop",
                params={"user_id": event.user_id, "kungfu_id": kungfu_id, "all_delete": True},
            ).get()
        ).json()
    except Exception:
        await remove_all_calculator_loop_matcher.finish("循环删除失败，请确认 calculator 服务可用后重试！")
    if result.get("code") == 200:
        await remove_all_calculator_loop_matcher.finish(f"已删除 {kungfu.name or query} 的全部自定义循环！")
    await remove_all_calculator_loop_matcher.finish("循环删除失败！" + str(result.get("msg", "")))

def check_jcl_name(filename: str, prefix: str) -> bool:
    if not filename.startswith(prefix):
        return False
    pattern = re.compile(
        r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-[\u4e00-\u9fff·\d]+(?:\(\d+\))?-[\u4e00-\u9fff·\d]+(?:\(\d+\))?\.jcl$"
    )
    return bool(pattern.match(filename[4:]))


jcl_equipment_import_lock = asyncio.Lock()


def _save_jcl_equipment(instance: JX3PlayerAttribute) -> None:
    instance.validate()
    instance.save()


async def _import_jcl_equipment(url: str) -> tuple[int, int]:
    response = await Request(url).get(timeout=600)
    jcl_text = await asyncio.to_thread(
        response.content.decode,
        "gbk",
        "replace"
    )
    attributes_data = await JX3PlayerAttribute.from_jcl(jcl_text)
    saved = 0
    failed = 0
    async with jcl_equipment_import_lock:
        for instance in attributes_data:
            try:
                await asyncio.to_thread(_save_jcl_equipment, instance)
                saved += 1
            except Exception as exc:
                failed += 1
                logger.warning(
                    f"JCL 本地装备保存失败：{instance.name}"
                    f"（{instance.global_role_id}）：{exc}"
                )
    return saved, failed

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
    elif check_jcl_name(event.file.name, "DPS-"):
        analyzer = DPSAnalyze
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
    elif check_jcl_name(event.file.name, "LNX-"):
        analyzer = LNXAnalyze
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
        equipment_import_task = asyncio.create_task(_import_jcl_equipment(url))
        try:
            try:
                image = await analyzer(event.file.name[4:], url, is_anonymous, event.user_id)
                await bot.send_group_msg(group_id=event.group_id, message=Message(image))
            except json.decoder.JSONDecodeError:
                await bot.send_group_msg(group_id=event.group_id, message="啊哦，音卡的服务器目前似乎暂时有些小问题，请稍后再使用JCL分析？")
        finally:
            try:
                saved, failed = await equipment_import_task
                logger.info(f"JCL 本地装备导入完成：成功 {saved} 条，失败 {failed} 条")
            except Exception as exc:
                logger.warning(f"JCL 本地装备导入失败：{exc}")
