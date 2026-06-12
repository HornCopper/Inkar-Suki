from pathlib import Path
from typing import Any, cast, Callable
from nonebot import on_command
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
from src.utils.database.player import search_player, get_uid_data
from src.utils.database.attributes import JX3PlayerAttribute
from src.utils.permission import check_permission, denied

from src.plugins.notice import notice
from src.plugins.jx3.calculator.compare import EquipInfo, get_equip_list
from src.plugins.preferences.app import Preference
from src.plugins.jx3.equip.equip_config import get_equip_image

from .jx3box import JX3BOXCalculator
from .base import FORMATIONS, FULL_INCOME_WITH_CONSUMABLES, get_calculator_income_codes, normalize_calculator_jcl_data
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
SPECIAL_PVE_KUNGFU_TAGS = {
    10014: "QCPVE",
    10015: "JCPVE",
    10224: "JYPVE",
    10225: "TLPVE",
    10821: "WXPVE",
}

DEFAULT_DAMAGE_TIMELINE_BIN_SIZE = 2.5
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
    "格式：<提交属性 区服 角色ID 心法名称>\n"
    "然后粘贴导出的装备码即可完成提交。\n\n"
    "计算器唤醒指令\n"
    "T心法及双心法（如气纯、剑纯等）需要添加对应前缀，所有后缀均不写心法名称。\n"
    "指令格式：\n"
    "<T计算器 区服 角色ID>\n"
    "<QC/JY/TL计算器 区服 角色ID>\n\n"
    "其余心法无需加前缀和心法名称，直接使用：\n"
    "<计算器 区服 角色ID>\n\n"
    "装备评级\n"
    "格式：<装备评级 区服 角色ID 心法名称>\n\n"
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
    html_source = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
body { margin: 0; background: #edf1f7; font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif; color: #202638; }
.guide { width: 920px; box-sizing: border-box; padding: 34px; background: #f7f9fc; }
.header { padding: 28px 30px; background: #243149; color: #fff; border-radius: 8px; }
.eyebrow { font-size: 18px; color: #b9c7dc; font-weight: 700; }
.title { margin-top: 8px; font-size: 34px; line-height: 1.22; font-weight: 900; }
.subtitle { margin-top: 12px; font-size: 18px; color: #d8e0ed; line-height: 1.6; }
.section { margin-top: 18px; padding: 24px 26px; background: #fff; border: 1px solid #e0e5ef; border-radius: 8px; }
.section-title { font-size: 24px; font-weight: 900; margin-bottom: 18px; color: #1f2937; }
.section-subtitle { margin-top: -8px; margin-bottom: 15px; color: #5d687a; font-size: 17px; line-height: 1.55; }
.image-frame { overflow: hidden; border-radius: 8px; border: 1px solid #d8e0ec; background: #111827; }
.guide-image { display: block; width: 100%; height: auto; }
.caption { margin-top: 10px; color: #5f6878; font-size: 16px; line-height: 1.55; }
.steps { display: grid; gap: 12px; }
.step { display: grid; grid-template-columns: 42px 1fr; gap: 14px; align-items: start; }
.num { width: 42px; height: 42px; border-radius: 50%; background: #2f6bff; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 900; }
.text { min-height: 42px; display: flex; align-items: center; font-size: 19px; line-height: 1.62; color: #333b4d; }
.code { margin: 10px 0 4px; padding: 13px 15px; border-radius: 6px; background: #f1f5fb; border: 1px solid #d9e2ef; font-size: 20px; font-weight: 800; color: #1d2b44; }
.example { display: inline-block; margin: 6px 10px 0 0; padding: 9px 12px; background: #fff8e6; border: 1px solid #f2d17a; border-radius: 6px; color: #62430b; font-size: 17px; font-weight: 700; }
.note { margin-top: 16px; padding: 14px 16px; background: #edf7ef; border: 1px solid #b7dfbf; border-radius: 6px; color: #275431; font-size: 18px; line-height: 1.6; font-weight: 700; }
.usage { display: grid; gap: 10px; }
.usage-item { padding: 13px 15px; background: #f7f9fc; border: 1px solid #e0e5ef; border-radius: 6px; font-size: 18px; line-height: 1.6; color: #343d50; }
.command { color: #1f57d6; font-weight: 900; }
.footer { margin-top: 16px; color: #697386; font-size: 15px; text-align: right; }
</style>
</head>
<body>
<div class="guide">
  <div class="header">
    <div class="eyebrow">自定义循环 help</div>
    <div class="title">如何制作一个专属于自己的 JCL 计算器循环</div>
    <div class="subtitle">按要求录制木桩 JCL，上传群文件后即可作为自己的计算器循环使用。</div>
  </div>
  <div class="section">
    <div class="section-title">制作 JCL</div>
    <div class="steps">
      <div class="step"><div class="num">1</div><div class="text">先按照图片这样勾选设置。</div></div>
      <div class="step"><div class="num">2</div><div class="text">去木桩面前。</div></div>
      <div class="step"><div class="num">3</div><div class="text">开始打。</div></div>
      <div class="step"><div class="num">4</div><div class="text">打到你认为 OK 的时间，点伤害统计清空（用来验证 DPS 是否正确），随后停手 F1 选中自己。</div></div>
      <div class="step"><div class="num">5</div><div class="text">点 JCL 文件位置，找到你刚刚打的木桩 JCL 文件。</div></div>
      <div class="step"><div class="num">6</div><div class="text">按下面格式命名：</div></div>
    </div>
    <div class="code">CAL-心法名-加速阈值-紫武/橙武-循环名.jcl</div>
    <div class="example">CAL-隐龙诀-30158-紫武-测试1.jcl</div>
    <div class="example">CAL-莫问-19285-橙武-测试2.jcl</div>
    <div class="steps" style="margin-top: 16px;">
      <div class="step"><div class="num">7</div><div class="text">上传群文件。</div></div>
    </div>
    <div class="note">至此，JCL 已经导入成功，接下来是计算。</div>
  </div>
  <div class="section">
    <div class="section-title">JCL 导出方法</div>
    <div class="section-subtitle">打开插件集的角色统计界面，切到装备统计页，点击右上角导出。弹出的文本内容用于确认当前装备数据；JCL 文件本体仍按上面的步骤从 JCL 文件位置找到并上传。</div>
    <div class="image-frame"><img class="guide-image" src="__JCL_EXPORT_IMAGE__"></div>
    <div class="caption">图中红框位置：装备统计页签与导出按钮。</div>
  </div>
  <div class="section">
    <div class="section-title">使用自定义循环</div>
    <div class="usage">
      <div class="usage-item">1. 发送 <span class="command">偏好 计算器来源 自定义</span> 可以使用上传的 JCL。</div>
      <div class="usage-item">2. 发送 <span class="command">偏好 计算器来源 公用</span> 可以恢复使用公用循环库。</div>
      <div class="usage-item">3. 按原本的计算器命令正常使用即可，包括 T计算器、DPS计算器、装备对比等均可。</div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">提交公有循环</div>
    <div class="usage">
      <div class="usage-item">1. 发送 <span class="command">提交公有循环</span>，机器人会返回你上传过的自定义循环列表；也可以发送 <span class="command">提交公有循环 心法名</span> 只看指定心法。</div>
      <div class="usage-item">2. 发送要提交的编号后，循环会进入审批群待审；审批通过后会移动到公用循环库。</div>
      <div class="usage-item">3. 示例：<span class="command">提交公有循环 莫问</span>，列表返回后发送 <span class="command">1</span>。</div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">变更循环名字</div>
    <div class="usage">
      <div class="usage-item">1. 发送 <span class="command">循环改名 心法名</span>，机器人会列出你提供的公有循环和对应私有循环。</div>
      <div class="usage-item">2. 发送要改名的编号后，再发送新的循环名；只会变更文件名里的循环名部分。</div>
      <div class="usage-item">3. 拥有改名权限的用户可发送 <span class="command">循环改名 QQ号 心法名</span> 变更指定用户提供的循环。</div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">删除自定义循环</div>
    <div class="usage">
      <div class="usage-item">1. 发送 <span class="command">删除循环 心法名</span>，机器人会返回该心法循环列表；再发送编号删除单个或多个循环。</div>
      <div class="usage-item">2. 发送 <span class="command">删除循环all 心法名</span>，删除该心法下你上传的全部自定义循环。</div>
      <div class="usage-item">3. 示例：<span class="command">删除循环 莫问</span>，列表返回后发送 <span class="command">1,2</span>；或发送 <span class="command">删除循环all 莫问</span>。</div>
    </div>
  </div>
  <div class="footer">命令：自定义循环 help</div>
</div>
</body>
</html>
""".replace("__JCL_EXPORT_IMAGE__", html.escape(jcl_export_image, quote=True))
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


async def _special_pve_tag_options(global_role_id: int) -> list[dict[str, Any]]:
    all_equips = await JX3PlayerAttribute.from_database(global_role_id, "", True)
    if not all_equips:
        return []

    latest_by_kungfu: dict[int, JX3PlayerAttribute] = {}
    for equip in all_equips:
        kungfu_id = int(equip.kungfu_id)
        if equip.tag != "PVE" or kungfu_id not in SPECIAL_PVE_KUNGFU_TAGS:
            continue
        current = latest_by_kungfu.get(kungfu_id)
        if current is None or equip.timestamp > current.timestamp:
            latest_by_kungfu[kungfu_id] = equip

    options: list[dict[str, Any]] = []
    for kungfu_id, equip in sorted(latest_by_kungfu.items(), key=lambda item: item[1].timestamp, reverse=True):
        kungfu = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True)
        options.append(
            {
                "tag": SPECIAL_PVE_KUNGFU_TAGS[kungfu_id],
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
    options = await _special_pve_tag_options(global_role_id)
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


def _timeline_loop_entries(
    loops: dict[str, dict[str, str]],
    section: str,
    user_id: int,
) -> list[dict[str, Any]]:
    return [
        {
            "display_name": loop_name,
            "section": section,
            "user_id": user_id,
            **loop_data,
        }
        for loop_name, loop_data in loops.items()
    ]


async def _calculator_loop_entries(
    instance: UniversalCalculator | JX3BOXCalculator,
    user_id: int,
    is_custom: bool,
) -> list[dict[str, Any]] | str:
    if is_custom:
        public_loops = await instance.get_loop(0)
        custom_loops = await instance.get_loop(user_id)
        loop_entries: list[dict[str, Any]] = []
        if not isinstance(public_loops, str):
            loop_entries.extend(_timeline_loop_entries(public_loops, "公有循环", 0))
        if not isinstance(custom_loops, str):
            loop_entries.extend(_timeline_loop_entries(custom_loops, "自定义循环", user_id))
        if loop_entries:
            return loop_entries
        return "未找到可用的公有循环或自定义循环，请检查计算器循环库或上传自定义 JCL！\n切换方式：发送「偏好 计算器来源 公用」"

    loops = await instance.get_loop(0)
    if isinstance(loops, str):
        return "该玩家下线时的心法当前尚未实现计算器，可尝试使用指定计算器（如有）或等待该心法支持！\n也可能是当前使用的计算器循环库中并无该心法，请切换公用循环库或自定义循环库，详情见「偏好」。"
    return _timeline_loop_entries(loops, "", 0)


def _format_calculator_loop_selection(entries: list[dict[str, Any]], prompt: str = "请选择计算循环！") -> str:
    msg = prompt
    current_section = ""
    for index, entry in enumerate(entries, start=1):
        section = str(entry.get("section") or "")
        if section and section != current_section:
            msg += f"\n【{section}】"
            current_section = section
        msg += f"\n{index}. {entry.get('display_name') or '未命名循环'}"
    return msg


def _format_timeline_loop_selection(entries: list[dict[str, Any]], *, compare: bool) -> str:
    msg = "请选择要对比的计算循环，支持空格或逗号分隔！" if compare else "请选择计算循环！"
    return _format_calculator_loop_selection(entries, msg)


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
    loop_entries = await _calculator_loop_entries(instance, event.user_id, is_custom)
    if isinstance(loop_entries, str):
        await matcher.finish(loop_entries)
    state["timeline_loops"] = loop_entries
    state["timeline_instance"] = instance
    state["timeline_is_custom"] = is_custom
    state["timeline_compare"] = compare
    state["timeline_bin_size"] = bin_size
    await matcher.send(_format_timeline_loop_selection(loop_entries, compare=compare))


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
    loops: list[dict[str, Any]] = state["timeline_loops"]
    instance: UniversalCalculator | JX3BOXCalculator = state["timeline_instance"]
    compare = bool(state.get("timeline_compare"))
    parsed = _parse_timeline_selection(selection.extract_plain_text(), len(loops), compare=compare)
    if isinstance(parsed, str):
        await matcher.finish(parsed)
    await matcher.send("正在演算中，请稍候……")
    user_id = event.user_id if state.get("timeline_is_custom") else 0
    bin_size = float(state.get("timeline_bin_size", DEFAULT_DAMAGE_TIMELINE_BIN_SIZE))
    data = await _request_damage_timeline(instance, loops, parsed, user_id, bin_size)
    if isinstance(data, str):
        await matcher.finish(data)
    if state.get("timeline_pzid", 0) != 0:
        await matcher.send(ms.image(await get_equip_image(str(state["timeline_pzid"]))))
    await matcher.finish(await _render_damage_timeline_image(data, instance, compare=compare))


rd_analysis_support_matcher = on_command(
    "jx3_rd_analysis_support",
    aliases={"RD分析支持", "rd分析支持", "Rd分析支持"},
    priority=5,
    force_whitespace=True,
)


@rd_analysis_support_matcher.handle()
async def _():
    await rd_analysis_support_matcher.finish(RD_ANALYSIS_SUPPORT_TEXT)


jcl_analysis_help_matcher = on_command(
    "jx3_jcl_analysis",
    aliases={"JCL分析", "jcl分析", "Jcl分析"},
    priority=5,
    force_whitespace=True,
)


@jcl_analysis_help_matcher.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    query = args.extract_plain_text().strip().lower()
    if query not in {"", "help", "帮助", "参数", "示例"}:
        await matcher.finish("参考格式：JCL分析 help")
    await matcher.finish(_jcl_analysis_help_message())


custom_loop_help_matcher = on_command(
    "jx3_custom_loop_help",
    aliases={"自定义循环"},
    priority=5,
    force_whitespace=True,
)


@custom_loop_help_matcher.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    query = args.extract_plain_text().strip().lower()
    if query not in {"", "help", "帮助", "参数", "示例"}:
        await matcher.finish("参考格式：自定义循环 help")
    await matcher.finish(await _render_custom_loop_help_image())


calculator_support_matcher = on_command(
    "jx3_calculator_support",
    aliases={"计算器支持", "计算器心法", "计算器支持心法"},
    priority=5,
    force_whitespace=True,
)


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


equipment_rating_support_matcher = on_command(
    "jx3_equipment_rating_support",
    aliases={"装备评级支持", "装备评级心法", "装备评级支持心法"},
    priority=5,
    force_whitespace=True,
)


@equipment_rating_support_matcher.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    await equipment_rating_module.handle_equipment_rating_support(matcher, args)


equipment_rating_matcher = on_command(
    "jx3_equipment_rating",
    aliases={"装备评级"},
    priority=5,
    force_whitespace=True,
)


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
    aliases=_prefixed_command_aliases("循环曲线", CALCULATOR_PREFIXES),
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
    aliases=_prefixed_command_aliases("循环对比", CALCULATOR_PREFIXES),
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


calc_matcher = on_command(
    "jx3_calculator",
    aliases={"计算器", "T计算器", "QC计算器", "JC计算器", "TL计算器", "JY计算器", "WX计算器"},
    priority=5,
    force_whitespace=True,
)


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
    elif len(arg) == 2:
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
            instance = await UniversalCalculator.with_global_role_id(int(context["global_role_id"]), selected_tag)
        else:
            instance = await UniversalCalculator.with_name(str(context["name"]), str(context["server"]), selected_tag)
        if isinstance(instance, str):
            await calc_matcher.finish(instance)
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

equip_compare = on_command(
    "jx3_equip_compare",
    aliases={"装备对比", "T装备对比", "QC装备对比", "JC装备对比", "TL装备对比", "JY装备对比", "WX装备对比"},
    priority=5,
    force_whitespace=True,
)

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


submit_public_loop_matcher = on_command(
    "jx3_submit_public_loop",
    aliases={"提交公有循环"},
    priority=5,
    force_whitespace=True,
)


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


public_loop_approval_config_matcher = on_command(
    "jx3_public_loop_approval_config",
    aliases={"公有循环审批设置", "公有循环审批配置"},
    priority=5,
    force_whitespace=True,
)


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


approve_public_loop_matcher = on_command(
    "jx3_approve_public_loop",
    aliases={"公有循环审批", "审批公有循环"},
    priority=5,
    force_whitespace=True,
)


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


rename_calculator_loop_matcher = on_command(
    "jx3_rename_calc_loop",
    aliases={"循环改名", "改循环名", "修改循环名", "变更循环名字"},
    priority=5,
    force_whitespace=True,
)


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


remove_calculator_loop_matcher = on_command(
    "jx3_rm_calc_loop",
    aliases={"删除循环"},
    priority=5,
    force_whitespace=True,
)


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


remove_all_calculator_loop_matcher = on_command(
    "jx3_rm_all_calc_loop",
    aliases={"删除循环all"},
    priority=5,
    force_whitespace=True,
)


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
