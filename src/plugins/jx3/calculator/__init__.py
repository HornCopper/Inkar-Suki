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
from src.utils.generate import generate
from src.utils.database.player import search_player, get_uid_data
from src.utils.database.attributes import JX3PlayerAttribute
from src.utils.permission import check_permission, denied

from src.plugins.notice import notice
from src.plugins.jx3.calculator.compare import EquipInfo, get_equip_list
from src.plugins.preferences.app import Preference
from src.plugins.jx3.equip.equip_config import get_equip_image

from .jx3box import JX3BOXCalculator
from .base import FORMATIONS, FULL_INCOME_WITH_CONSUMABLES, get_calculator_income_codes
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
import html


def _prefixed_command_aliases(base_command: str, prefixes: tuple[str, ...]) -> set[str]:
    aliases = {base_command}
    for prefix in prefixes:
        variants = {""}
        for char in prefix:
            variants = {variant + letter for variant in variants for letter in {char.lower(), char.upper()}}
        aliases.update(f"{variant}{base_command}" for variant in variants)
    return aliases


CALCULATOR_PREFIXES = ("T", "QC", "JC", "TL", "JY", "WX")

calc_matcher = on_command("jx3_calculator", aliases={"计算器", "T计算器", "QC计算器", "JC计算器", "TL计算器", "JY计算器", "WX计算器"}, priority=5, force_whitespace=True)
calculator_support_matcher = on_command("jx3_calculator_support", aliases={"计算器支持", "计算器心法", "计算器支持心法"}, priority=5, force_whitespace=True)
equipment_rating_matcher = on_command("jx3_equipment_rating", aliases={"装备评级"}, priority=5, force_whitespace=True)
equipment_rating_support_matcher = on_command("jx3_equipment_rating_support", aliases={"装备评级支持", "装备评级心法", "装备评级支持心法"}, priority=5, force_whitespace=True)
rd_analysis_support_matcher = on_command("jx3_rd_analysis_support", aliases={"RD分析支持", "rd分析支持", "Rd分析支持"}, priority=5, force_whitespace=True)
timeline_matcher = on_command(
    "jx3_damage_timeline",
    aliases=_prefixed_command_aliases("循环曲线", CALCULATOR_PREFIXES),
    priority=5,
    force_whitespace=True,
)
timeline_compare_matcher = on_command(
    "jx3_damage_timeline_compare",
    aliases=_prefixed_command_aliases("循环对比", CALCULATOR_PREFIXES),
    priority=5,
    force_whitespace=True,
)

DEFAULT_DAMAGE_TIMELINE_BIN_SIZE = 2.5

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
) -> UniversalCalculator | JX3BOXCalculator:
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
        instance = await UniversalCalculator.with_global_role_id(int(global_role_id), tag)
        if isinstance(instance, str):
            await matcher.finish(instance)
        return instance

    server = Server(server, event.group_id).server
    if server is None:
        await matcher.finish(PROMPT.ServerNotExist)
    instance = await UniversalCalculator.with_name(name, server, tag)
    if isinstance(instance, str):
        await matcher.finish(instance)
    return instance


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


async def _prepare_timeline_selection(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    args: Message,
    cmd: str,
    *,
    compare: bool,
) -> None:
    raw_text = args.extract_plain_text().strip()
    if raw_text == "":
        if compare:
            await matcher.finish(TIMELINE_COMPARE_HELP_TEXT)
        await matcher.finish(TIMELINE_HELP_TEXT)
    if not compare and raw_text.lower() in {"help", "帮助", "参数", "示例"}:
        await matcher.finish(TIMELINE_HELP_TEXT)
    if compare and raw_text.lower() in {"help", "帮助", "参数", "示例"}:
        await matcher.finish(TIMELINE_COMPARE_HELP_TEXT)
    arg, bin_size = _parse_timeline_command_args(raw_text)
    if isinstance(bin_size, str):
        await matcher.finish(bin_size)
    if compare and len(arg) not in [1, 2]:
        await matcher.finish(TIMELINE_COMPARE_HELP_TEXT)
    instance = await _resolve_timeline_instance(event, matcher, state, arg, cmd)
    is_custom = _apply_calculator_preferences(event, instance)
    loops = await instance.get_loop(event.user_id if is_custom else 0)
    if isinstance(loops, str):
        unsupported_msg = "该玩家下线时的心法当前尚未实现计算器，可尝试使用指定计算器（如有）或等待该心法支持！\n也可能是当前使用的计算器循环库中并无该心法，请切换公用循环库或自定义循环库，详情见「偏好」。"
        if is_custom:
            unsupported_msg = "未找到已上传的该心法 JCL，请切换至公用循环库或自行上传该心法循环！\n切换方式：发送「偏好 计算器来源 公用」"
        await matcher.finish(unsupported_msg)
    state["timeline_loops"] = loops
    state["timeline_instance"] = instance
    state["timeline_is_custom"] = is_custom
    state["timeline_compare"] = compare
    state["timeline_bin_size"] = bin_size
    msg = "请选择要对比的计算循环，支持空格或逗号分隔！" if compare else "请选择计算循环！"
    for index, loop_name in enumerate(loops, start=1):
        msg += f"\n{index}. {loop_name}"
    await matcher.send(msg)


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
    loops: dict[str, dict[str, str]],
    selected_indices: list[int],
    user_id: int,
    bin_size: float,
) -> dict[str, Any] | str:
    loop_names = list(loops)
    selected_loops = []
    for index in selected_indices:
        name = loop_names[index - 1]
        selected_loops.append({"name": name, "index": index, **loops[name]})
    jcl_data = instance.jcl_data if getattr(instance, "jcl_data", None) else instance.equip_data.equip_lines
    kungfu_id = instance.calculator_kungfu_id
    payload = {
        "kungfu_id": kungfu_id,
        "jcl_data": jcl_data,
        "loops": selected_loops,
        "full_income": instance.income_list + instance.formation_list,
        "user_id": user_id,
        "bin_size": bin_size,
    }
    try:
        response = await Request(f"{Config.jx3.api.calculator_url}/damage_timeline", params=payload).post(timeout=120)
        result = response.json()
    except Exception as exc:
        return f"循环曲线计算失败：{exc}"
    if result.get("code") != 200:
        return str(result.get("msg") or "循环曲线计算失败。")
    return result["data"]


def _format_compact_number(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "0"
    if abs(number) >= 100000000:
        return f"{number / 100000000:.2f}亿"
    if abs(number) >= 10000:
        return f"{number / 10000:.1f}万"
    return f"{int(number):,}"


def _format_seconds(value: float) -> str:
    if abs(value - round(value)) < 0.05:
        return f"{int(round(value))}s"
    return f"{value:.1f}s"


def _smooth_path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    if len(points) == 1:
        x, y = points[0]
        return f"M{x:.2f},{y:.2f}"
    path = [f"M{points[0][0]:.2f},{points[0][1]:.2f}"]
    for index in range(len(points) - 1):
        p0 = points[index - 1] if index > 0 else points[index]
        p1 = points[index]
        p2 = points[index + 1]
        p3 = points[index + 2] if index + 2 < len(points) else p2
        c1x = p1[0] + (p2[0] - p0[0]) / 6
        c1y = p1[1] + (p2[1] - p0[1]) / 6
        c2x = p2[0] - (p3[0] - p1[0]) / 6
        c2y = p2[1] - (p3[1] - p1[1]) / 6
        path.append(f"C{c1x:.2f},{c1y:.2f} {c2x:.2f},{c2y:.2f} {p2[0]:.2f},{p2[1]:.2f}")
    return " ".join(path)


def _series_points(
    series: dict[str, Any],
    key: str,
    width: int,
    height: int,
    max_value: float,
    max_second: float,
    source_key: str,
) -> list[tuple[float, float]]:
    bins = series.get("adjusted", {}).get(source_key) or []
    x_denominator = max(1, max_second)
    points = []
    for item in bins:
        second = float(item.get("second", 0) or 0)
        value = float(item.get(key, 0) or 0)
        x = second / x_denominator * width
        y = height - (value / max_value * height if max_value else 0)
        points.append((x, y))
    return points


def _peak_point(
    series: dict[str, Any],
    width: int,
    height: int,
    max_value: float,
    max_second: float,
    source_key: str,
) -> tuple[float, float, dict[str, Any]] | None:
    bins = series.get("adjusted", {}).get(source_key) or []
    if not bins:
        return None
    peak = max(bins, key=lambda item: int(item.get("damage_per_second_bin", 0) or 0))
    all_points = _series_points(series, "damage_per_second_bin", width, height, max_value, max_second, source_key)
    if not all_points:
        return None
    peak_index = bins.index(peak)
    x, y = all_points[peak_index]
    return x, y, peak


def _buff_overlays_svg(
    buff_overlays: list[dict[str, Any]],
    width: int,
    height: int,
    max_second: float,
) -> str:
    if not buff_overlays:
        return ""
    frames = []
    labels = []
    for overlay in buff_overlays:
        try:
            start = max(0.0, float(overlay.get("start", 0) or 0))
            end = min(max_second, float(overlay.get("end", 0) or 0))
        except (TypeError, ValueError):
            continue
        if end <= start:
            continue
        row = max(0, int(overlay.get("row", 0) or 0))
        color = html.escape(str(overlay.get("color") or "#64748B"))
        label = html.escape(str(overlay.get("label") or ""))
        x = start / max_second * width
        frame_width = max(1, (end - start) / max_second * width)
        frames.append(
            f'<rect x="{x:.2f}" y="0" width="{frame_width:.2f}" height="{height}" '
            f'rx="4" fill="{color}" stroke="{color}" class="buff-frame"/>'
        )
        if label:
            label_x = x + 6
            anchor = "start"
            if label_x > width - 90:
                label_x = width - 6
                anchor = "end"
            label_y = min(height - 8, 18 + row * 18)
            labels.append(
                f'<text x="{label_x:.2f}" y="{label_y:.2f}" text-anchor="{anchor}" '
                f'class="buff-frame-label" fill="{color}">{label}</text>'
            )
    return "".join(frames + labels)


def _chart_svg(
    series_list: list[dict[str, Any]],
    key: str,
    colors: list[str],
    title: str,
    width: int,
    height: int,
    mark_peak: bool = False,
    source_key: str = "bins",
    buff_overlays: list[dict[str, Any]] | None = None,
) -> str:
    max_value = max(
        (
            float(item.get(key, 0) or 0)
            for series in series_list
            for item in (series.get("adjusted", {}).get(source_key) or [])
        ),
        default=1,
    )
    max_value = max(max_value, 1)
    max_bin_second = max(
        (
            float(item.get("second", 0) or 0)
            for series in series_list
            for item in (series.get("adjusted", {}).get(source_key) or [])
        ),
        default=0,
    )
    terminal_second = max(
        (float((series.get("adjusted") or {}).get("battle_time", 0) or 0) for series in series_list),
        default=0,
    )
    terminal_tick_second = max(1, max_bin_second, terminal_second)
    max_second = terminal_tick_second + max(5, terminal_tick_second * 0.04)
    grid_lines = []
    for ratio in [0, 0.25, 0.5, 0.75, 1]:
        y = height - ratio * height
        value = max_value * ratio
        grid_lines.append(
            f'<line x1="0" y1="{y:.2f}" x2="{width}" y2="{y:.2f}" stroke="#e6e8ee" stroke-width="1"/>'
            f'<text x="-12" y="{y + 4:.2f}" text-anchor="end" class="axis-label">{html.escape(_format_compact_number(value))}</text>'
        )
    time_ticks = []
    tick = 0
    while tick < terminal_tick_second:
        time_ticks.append(float(tick))
        tick += 15
    terminal_tick_x = terminal_tick_second / max_second * width
    time_ticks = [
        tick_second
        for tick_second in time_ticks
        if abs(tick_second / max_second * width - terminal_tick_x) >= 48
    ]
    if not any(abs(t - terminal_tick_second) < 0.05 for t in time_ticks):
        time_ticks.append(terminal_tick_second)
    axis_ticks = []
    for tick_second in time_ticks:
        x = tick_second / max_second * width
        anchor = "middle"
        if x < 12:
            anchor = "start"
        elif x > width - 12:
            anchor = "end"
        axis_ticks.append(
            f'<line x1="{x:.2f}" y1="{height}" x2="{x:.2f}" y2="{height + 7}" stroke="#b7bcc8" stroke-width="1"/>'
            f'<text x="{x:.2f}" y="{height + 24}" text-anchor="{anchor}" class="axis-label">{html.escape(_format_seconds(tick_second))}</text>'
        )
    overlay_bands = _buff_overlays_svg(buff_overlays or [], width, height, max_second)
    paths = []
    peaks = []
    for index, series in enumerate(series_list):
        color = colors[index % len(colors)]
        points = _series_points(series, key, width, height, max_value, max_second, source_key)
        path = _smooth_path(points)
        paths.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
        if mark_peak:
            peak = _peak_point(series, width, height, max_value, max_second, source_key)
            if peak is not None:
                x, y, item = peak
                peaks.append(
                    f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="{color}" stroke="#fff" stroke-width="2"/>'
                    f'<text x="{min(width - 8, x + 10):.2f}" y="{max(16, y - 10):.2f}" class="peak-label" fill="{color}">'
                    f'{html.escape(series.get("label", ""))}峰值 {_format_compact_number(item.get("damage_per_second_bin"))}</text>'
                )
    return (
        f'<div class="chart-title">{html.escape(title)}</div>'
        f'<svg viewBox="-78 -10 {width + 96} {height + 40}" class="chart">'
        + "".join(grid_lines)
        + overlay_bands
        + "".join(paths)
        + "".join(peaks)
        + f'<line x1="0" y1="{height}" x2="{width}" y2="{height}" stroke="#b7bcc8" stroke-width="1.5"/>'
        + "".join(axis_ticks)
        + '</svg>'
    )


async def _render_damage_timeline_image(
    data: dict[str, Any],
    instance: UniversalCalculator | JX3BOXCalculator,
    *,
    compare: bool,
) -> Any:
    series_list = data.get("series") or []
    colors = ["#2F6BFF", "#E05252", "#18A058", "#8B5CF6", "#F59E0B", "#0EA5A4"]
    name, server = getattr(instance, "info", ("", ""))
    kungfu = Kungfu.with_internel_id(instance.calculator_kungfu_id, convert_to_pc=True)
    title = "循环对比" if compare else "循环曲线"
    legend_items = []
    stat_cards = []
    for index, series in enumerate(series_list):
        color = colors[index % len(colors)]
        adjusted = series.get("adjusted") or {}
        dps = _format_compact_number(adjusted.get("dps"))
        label = html.escape(str(series.get("label") or index + 1))
        loop_name = html.escape(str(series.get("loop_name") or "未命名循环"))
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
    html_source = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ margin: 0; background: #edf1f7; font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif; color: #1f2430; }}
.canvas {{ width: 1040px; padding: 34px; background: #f7f9fc; }}
.header {{ display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 22px; }}
.title {{ font-size: 34px; font-weight: 800; }}
.subtitle {{ margin-top: 8px; color: #697386; font-size: 18px; }}
.badge {{ color: #fff; background: #263247; border-radius: 6px; padding: 8px 12px; font-weight: 700; }}
.panel {{ background: #fff; border: 1px solid #e2e6ef; border-radius: 8px; padding: 22px; margin-bottom: 18px; }}
.legend {{ display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 16px; }}
.legend-item {{ font-size: 16px; color: #4d5668; }}
.legend-item i {{ display: inline-block; width: 18px; height: 5px; border-radius: 5px; margin-right: 7px; vertical-align: middle; }}
.stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
.stat-card {{ border-left: 5px solid #2F6BFF; background: #fafbfe; border-radius: 6px; padding: 14px; }}
.stat-title {{ font-size: 18px; font-weight: 800; }}
.stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px 12px; margin-top: 10px; color: #566074; font-size: 14px; }}
.stat-grid b {{ color: #1f2430; }}
.chart-title {{ font-size: 21px; font-weight: 800; margin-bottom: 8px; }}
.chart {{ width: 100%; height: 350px; overflow: visible; }}
.axis-label {{ fill: #858da0; font-size: 13px; }}
.peak-label {{ font-size: 14px; font-weight: 700; }}
.buff-frame {{ fill-opacity: 0.1; stroke-opacity: 0.42; stroke-width: 1.4; }}
.buff-frame-label {{ font-size: 12px; font-weight: 800; opacity: 0.86; }}
</style>
</head>
<body>
<div class="canvas">
  <div class="header">
    <div>
      <div class="title">{html.escape(title)}</div>
      <div class="subtitle">{html.escape(server or "-")} · {html.escape(name or "-")} · {html.escape(kungfu.name or "未知心法")}</div>
    </div>
    <div class="badge">{html.escape(instance.income_ver or "无增益")} / {html.escape(instance.formation_name or "无阵眼")}</div>
  </div>
  <div class="panel">
    <div class="legend">{"".join(legend_items)}</div>
    <div class="stats">{"".join(stat_cards)}</div>
  </div>
  <div class="panel">{damage_chart}</div>
  <div class="panel">{dps_chart}</div>
</div>
</body>
</html>
"""
    return await generate(
        html_source,
        ".canvas",
        False,
        segment=True,
        full_screen=True,
        viewport={"width": 1100, "height": 1500},
    )


async def _finish_damage_timeline(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    selection: Message,
) -> None:
    if "timeline_loops" not in state or "timeline_instance" not in state:
        await matcher.finish("循环曲线/循环对比状态已失效，请重新发起命令！")
    loops: dict[str, dict[str, str]] = state["timeline_loops"]
    instance: UniversalCalculator | JX3BOXCalculator = state["timeline_instance"]
    compare = bool(state.get("timeline_compare"))
    parsed = _parse_timeline_selection(selection.extract_plain_text(), len(loops), compare=compare)
    if isinstance(parsed, str):
        await matcher.finish(parsed)
    await matcher.send("音卡正在努力演算中！")
    user_id = event.user_id if state.get("timeline_is_custom") else 0
    bin_size = float(state.get("timeline_bin_size", DEFAULT_DAMAGE_TIMELINE_BIN_SIZE))
    data = await _request_damage_timeline(instance, loops, parsed, user_id, bin_size)
    if isinstance(data, str):
        await matcher.finish(data)
    if state.get("timeline_pzid", 0) != 0:
        await matcher.send(ms.image(await get_equip_image(str(state["timeline_pzid"]))))
    await matcher.finish(await _render_damage_timeline_image(data, instance, compare=compare))


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


@timeline_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg(), cmd: str = RawCommand()):
    await _prepare_timeline_selection(event, matcher, state, args, cmd, compare=False)


@timeline_matcher.got("timeline_loop_order")
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, timeline_loop_order: Message = Arg()):
    await _finish_damage_timeline(event, matcher, state, timeline_loop_order)


@timeline_compare_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg(), cmd: str = RawCommand()):
    await _prepare_timeline_selection(event, matcher, state, args, cmd, compare=True)


@timeline_compare_matcher.got("timeline_loop_order")
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, timeline_loop_order: Message = Arg()):
    await _finish_damage_timeline(event, matcher, state, timeline_loop_order)


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
    income_code = get_calculator_income_codes(income_ver, instance.calculator_kungfu_id)
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
    income_code = get_calculator_income_codes(income_ver, int(str(kungfu_id)))
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
    income_code = get_calculator_income_codes(income_ver, int(str(kungfu_id)))
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
