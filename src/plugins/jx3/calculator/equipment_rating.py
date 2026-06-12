from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Template
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from src.config import Config
from src.const.jx3.kungfu import Kungfu
from src.const.jx3.server import Server
from src.const.path import ASSETS, TEMPLATES, build_path
from src.const.prompts import PROMPT
from src.utils.database.attributes import (
    JX3PlayerAttribute,
    TabCache,
    Talent,
    get_attr_name,
    split_display_attributes,
)
from src.utils.database.constant import (
    CRITICAL_DAMAGE_DIVISOR,
    CRITICAL_DIVISOR,
    OVERCOME_DIVISOR,
    STRAIN_DIVISOR,
)
from src.utils.database.player import get_uid_data, search_player
from src.utils.file import read
from src.utils.generate import generate
from src.utils.network import Request

from .base import normalize_calculator_jcl_data


RANK_ICON_FILES = {
    "ACE": "rank_ace.png",
    "S+": "rank_s_plus.png",
    "S": "rank_s.png",
    "A": "rank_a.png",
    "B": "rank_b.png",
    "C": "rank_c.png",
    "D": "rank_d.png",
}
RANK_THEMES = {
    "ACE": {"accent": "#ff304f", "light": "#ffd2da", "deep": "#8f0017", "rgb": "255 48 79"},
    "S+": {"accent": "#ff7a00", "light": "#ffd4a3", "deep": "#a83a00", "rgb": "255 122 0"},
    "S": {"accent": "#ffd24d", "light": "#fff1b6", "deep": "#9c6500", "rgb": "255 210 77"},
    "A": {"accent": "#a85cff", "light": "#efe0ff", "deep": "#5620b8", "rgb": "168 92 255"},
    "B": {"accent": "#3f8cff", "light": "#dceaff", "deep": "#0647ad", "rgb": "63 140 255"},
    "C": {"accent": "#22c76f", "light": "#d6f7e4", "deep": "#066437", "rgb": "34 199 111"},
    "D": {"accent": "#ffffff", "light": "#ffffff", "deep": "#9ca3af", "rgb": "190 196 206"},
}
EQUIPMENT_RATING_IMAGE_SEND_FAILED = (
    "装备评级图片已生成，但 QQ/NapCat 拒绝了图片上传。\n"
    "这通常是协议端富媒体上传失败，不是装备数据读取失败。请稍后重试，或联系维护者查看 NapCat 日志。"
)
EQUIPMENT_RATING_STARTED = "装备评级中，请稍等片刻！"
RATING_LOOP_LIST_KEYWORDS = {"评级列表", "循环列表", "JCL列表", "jcl列表"}
SPECIAL_PVE_KUNGFU_TAGS = {
    10014: "QCPVE",
    10015: "JCPVE",
    10224: "JYPVE",
    10225: "TLPVE",
    10821: "WXPVE",
}
EQUIPMENT_RATING_USAGE = (
    "装备评级使用步骤：\n"
    "1. 先提交属性：提交属性 <服务器> <角色名> <心法> <茗伊装备导出码>\n"
    "   例如：提交属性 剑胆琴心 倦收天 太虚剑意 <从茗伊复制的整段装备导出码>\n"
    "   注意：导出码与心法之间要有个空格\n"
    "2. 再执行评级：装备评级 <服务器> <角色名> [心法]\n"
    "   例如：装备评级 剑胆琴心 倦收天 太虚剑意\n"
    "3. 查看目前支持心法：装备评级支持 或 装备评级支持 <心法名>\n"
    "帮助：装备评级 help"
)
EQUIPMENT_RATING_HELP_KEYWORDS = {"help", "帮助", "？", "?"}
EQUIPMENT_RATING_DISTRIBUTION_PATH = build_path(
    ASSETS, ["source", "jx3", "equipment_rating_distribution.json"]
)


def _asset_uri(*parts: str) -> str:
    return Path(build_path(ASSETS, list(parts))).as_uri()


def _load_equipment_rating_distribution() -> dict[str, Any]:
    """读取预计算分布图索引；运行时只做静态资源查找，不做拟合计算。"""
    try:
        payload = json.loads(read(EQUIPMENT_RATING_DISTRIBUTION_PATH))
    except Exception:
        payload = {}
    return payload if isinstance(payload, dict) else {}


async def _render_equipment_rating_help_image():
    html_source = """
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<script>
window.MathJax = {
  tex: {
    inlineMath: [["\\\\(", "\\\\)"]],
    displayMath: [["\\\\[", "\\\\]"]]
  },
  svg: { fontCache: "global" }
};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  width: 980px;
  background: #f3f6f9;
  color: #202630;
  font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
}
.guide {
  width: 980px;
  padding: 36px;
  background: #f3f6f9;
}
.hero {
  padding: 30px 34px;
  border-radius: 8px;
  background: #243149;
  color: #fff;
}
.eyebrow {
  font-size: 18px;
  line-height: 1.25;
  color: #b9c7dc;
  font-weight: 800;
}
.title {
  margin-top: 8px;
  font-size: 34px;
  line-height: 1.2;
  font-weight: 900;
}
.subtitle {
  margin-top: 12px;
  max-width: 820px;
  font-size: 18px;
  line-height: 1.65;
  color: #d9e2ee;
}
.section {
  margin-top: 18px;
  padding: 24px 26px;
  border: 1px solid #e0e5ed;
  border-radius: 8px;
  background: #fff;
}
.section-title {
  margin-bottom: 14px;
  font-size: 24px;
  line-height: 1.25;
  font-weight: 900;
  color: #18202c;
}
.steps {
  display: grid;
  gap: 11px;
}
.step {
  display: grid;
  grid-template-columns: 34px 1fr;
  gap: 12px;
  align-items: start;
  font-size: 18px;
  line-height: 1.62;
  color: #333b4d;
}
.num {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2f6bff;
  color: #fff;
  font-size: 16px;
  font-weight: 900;
}
.command {
  display: inline-block;
  padding: 2px 7px;
  border-radius: 5px;
  background: #edf2ff;
  color: #2354d6;
  font-weight: 900;
}
.formula-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.formula-block {
  min-width: 0;
  padding: 18px;
  border: 1px solid #dde5ef;
  border-radius: 8px;
  background: #f8fafc;
}
.formula-title {
  font-size: 18px;
  font-weight: 900;
  color: #253044;
}
.formula {
  margin: 12px 0;
  min-height: 68px;
  overflow: hidden;
  color: #141a24;
}
.formula-note {
  font-size: 15px;
  line-height: 1.55;
  color: #5b6574;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
}
.chip {
  padding: 8px 12px;
  border-radius: 999px;
  background: #f5f7fb;
  border: 1px solid #dfe5ee;
  color: #303848;
  font-size: 16px;
  font-weight: 900;
}
.notice {
  padding: 18px 20px;
  border-left: 5px solid #ff8a00;
  background: #fff7e8;
  color: #563813;
  font-size: 18px;
  line-height: 1.65;
  font-weight: 800;
}
.footer {
  margin-top: 18px;
  color: #7a8392;
  font-size: 14px;
  text-align: right;
}
</style>
</head>
<body>
<div class="guide">
  <div class="hero">
    <div class="eyebrow">装备评级 help</div>
    <div class="title">评级给出的评分只能够衡量当前配装距离毕业的程度</div>
    <div class="subtitle">装备评级会在同一条评级 JCL、同一套默认评级增益下比较当前部位、空槽样本和候选装备，给出当前配装相对候选毕业解的接近程度。</div>
  </div>

  <div class="section">
    <div class="section-title">使用步骤</div>
    <div class="steps">
      <div class="step"><div class="num">1</div><div>先提交属性：<span class="command">提交属性 &lt;服务器&gt; &lt;角色名&gt; &lt;心法&gt; &lt;茗伊装备导出码&gt;</span></div></div>
      <div class="step"><div class="num">2</div><div>再执行评级：<span class="command">装备评级 &lt;服务器&gt; &lt;角色名&gt; &lt;心法&gt;</span></div></div>
      <div class="step"><div class="num">3</div><div>查看支持心法：<span class="command">装备评级支持</span> 或 <span class="command">装备评级支持 &lt;心法名&gt;</span></div></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">评级依据</div>
    <div class="steps">
      <div class="step"><div class="num">A</div><div>每个部位会计算三类样本：当前装备、去掉该部位后的空槽样本、同部位候选装备。</div></div>
      <div class="step"><div class="num">B</div><div>所有样本使用同一条评级 JCL 和默认评级增益，避免把循环和增益差异混进装备评分。</div></div>
      <div class="step"><div class="num">C</div><div>“最优候选”来自当前候选池中计算 DPS 最高的该部位装备；它是当前评级口径下的部位毕业参照。</div></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">计算公式</div>
    <div class="formula-grid">
      <div class="formula-block">
        <div class="formula-title">单件评分</div>
        <div class="formula">\\[
S_i = \\operatorname{clip}_{0}^{100}\\left(
\\frac{D_{\\mathrm{current}} - D_{\\mathrm{empty}, i}}
{D_{\\mathrm{best}, i} - D_{\\mathrm{empty}, i}} \\times 100
\\right)
\\]</div>
        <div class="formula-note">空槽 DPS 是该部位被移除后的基线；分数越高，代表该部位越接近当前候选池中的最优替换。</div>
      </div>
      <div class="formula-block">
        <div class="formula-title">配装总评</div>
        <div class="formula">\\[
S_{\\mathrm{total}} =
\\frac{\\sum_i S_i W_i}{\\sum_i W_i}
\\]</div>
        <div class="formula-note">\\(W_i\\) 是当前部位装分。总评按当前各部位装分加权平均，显示时保留 1 位小数。</div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">加速惩罚与补偿</div>
    <div class="formula-grid">
      <div class="formula-block">
        <div class="formula-title">修正系数</div>
        <div class="formula">\\[
\\Delta H = H_{\\mathrm{required}} - H_{\\mathrm{actual}}
\\]
\\[
C =
\\begin{cases}
\\max\\left(0, 1 - \\Delta H \\times \\frac{0.01}{3279}\\right), & \\Delta H > 0 \\\\
1 + (-\\Delta H) \\times \\frac{0.006}{3279}, & \\Delta H < 0 \\\\
1, & \\Delta H = 0
\\end{cases}
\\]</div>
        <div class="formula-note">缺加速按 1% / 3279 点折损；溢出加速按 0.6% / 3279 点补偿。</div>
      </div>
      <div class="formula-block">
        <div class="formula-title">修正后 DPS</div>
        <div class="formula">\\[
D_{\\mathrm{adjusted}} = \\left\\lfloor D_{\\mathrm{raw}} \\times C \\right\\rfloor
\\]</div>
        <div class="formula-note">单件评分中的 DPS 使用修正后 DPS。当前装备、空槽样本、候选装备都会先应用同一套加速修正规则。</div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">等级阈值</div>
    <div class="chips">
      <div class="chip">ACE ≥ 95</div>
      <div class="chip">S+ ≥ 90</div>
      <div class="chip">S ≥ 85</div>
      <div class="chip">A ≥ 80</div>
      <div class="chip">B ≥ 70</div>
      <div class="chip">C ≥ 60</div>
      <div class="chip">D ＜ 60</div>
    </div>
  </div>

  <div class="section">
    <div class="notice">该评级与实际 DPS 无单调性相关：高分不等于实际 DPS 必然更高，低分也不等于实际 DPS 必然更低。它只表示当前配装距离该心法、该评级循环、该候选池下毕业配装的接近程度。</div>
  </div>

  <div class="footer">命令：装备评级 help</div>
</div>
</body>
</html>
"""
    return await generate(
        html_source,
        ".guide",
        delay=800,
        segment=True,
        wait_for_network=True,
        viewport={"width": 980, "height": 2100},
    )


SLOT_DISPLAY_ORDER = [4, 3, 8, 12, 10, 11, 5, 9, 6, 7, 2, 0]
SLOT_NAME_OVERRIDES = {"上衣": "衣服"}
MAIN_ATTR_LABELS = {
    "atSpiritBase": "根骨",
    "atStrengthBase": "力道",
    "atAgilityBase": "身法",
    "atSpunkBase": "元气",
    "atVitalityBase": "体质",
}
HIDDEN_DETAIL_ATTRIBUTE_LABELS = {"化劲"}
HIDDEN_ATTRIBUTE_TEXTS = {
    "atPhysicsShieldBase",
    "atPhysicsshieldBase",
    "atMagicShield",
    "atInvalid",
    "atSInvalid",
    "atSkillEventHandler",
    "atSetEquipmentRecipe",
    "外防",
    "内防",
    "体质",
}
ATTRIBUTE_INCOME_DISPLAY_KEYS = {
    "Physics": (
        "atPhysicsAttackPowerBase",
        "atPhysicsCriticalStrike",
        "atPhysicsCriticalDamagePowerBase",
        "atPhysicsOvercomeBase",
        "atSurplusValueBase",
        "atStrainBase",
    ),
    "Magic": (
        "atMagicAttackPowerBase",
        "atMagicCriticalStrike",
        "atMagicCriticalDamagePowerBase",
        "atMagicOvercome",
        "atSurplusValueBase",
        "atStrainBase",
    ),
}


def _is_hidden_attribute_text(value: Any) -> bool:
    text = str(value or "").strip()
    if not text or text in HIDDEN_ATTRIBUTE_TEXTS:
        return True
    return text.startswith("at") and not get_attr_name(text)


def _short_attribute_text(value: Any) -> str:
    text = str(value or "").strip()
    return get_attr_name(text) or text


def _to_float(value: Any, default: float = 0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _format_number(value: Any) -> str:
    try:
        return f"{int(float(value)):,}"
    except (TypeError, ValueError):
        return "0"


def _format_haste(value: Any) -> str:
    try:
        haste = float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        haste = 0
    return f"{int(haste)} / {_haste_level(haste)}"


def _format_plain_int(value: Any) -> str:
    try:
        return str(int(float(value)))
    except (TypeError, ValueError):
        return "0"


def _format_signed(value: Any) -> str:
    try:
        return f"{int(float(value)):+,}"
    except (TypeError, ValueError):
        return "+0"


def _format_signed_float(value: Any) -> str:
    number = _to_float(value)
    if abs(number) < 0.05:
        return "+0"
    if abs(number) >= 10000:
        return f"{number / 10000:+.1f}万"
    if abs(number) >= 10:
        return f"{number:+,.0f}"
    return f"{number:+.1f}"


def _format_percent(value: Any) -> str:
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "0.0%"


async def _fetch_supported_equipment_rating_data(timeout: float = 8) -> dict[str, Any] | str:
    try:
        response = await Request(f"{Config.jx3.api.calculator_url}/equipment_rating/kungfus").get(timeout=timeout)
        if response.status_code == 404:
            return "装备评级支持心法查询失败：calculator 尚未加载支持心法接口，请重启 calculator 后重试。"
        if response.status_code >= 400:
            return f"装备评级支持心法查询失败：calculator 返回 HTTP {response.status_code}。"
        result = response.json()
    except Exception as exc:
        return f"装备评级支持心法查询失败：{exc}"
    if result.get("code") != 200:
        return result.get("msg", "装备评级支持心法查询失败。")
    return result.get("data") or {}


def _supported_kungfu_name(item: dict[str, Any]) -> str:
    kungfu_id = item.get("kungfu_id", 0)
    kungfu = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True)
    return str(item.get("name") or kungfu.name or "未知心法")


def _supported_kungfu_school(item: dict[str, Any]) -> str:
    kungfu = Kungfu.with_internel_id(item.get("kungfu_id", 0), convert_to_pc=True)
    return kungfu.school or "其他"


def _selected_rating_loop_text(item: dict[str, Any]) -> str:
    selected = item.get("selected") or {}
    parts = [
        str(selected.get("weapon") or "").strip(),
        str(selected.get("haste") or "").strip(),
        str(selected.get("loop") or "").strip(),
    ]
    return " · ".join(part for part in parts if part) or "未指定循环"


def _selected_jcl_record(item: dict[str, Any]) -> dict[str, Any]:
    selected = item.get("selected") or {}
    record = selected.get("jcl_record") or item.get("jcl_record") or {}
    return record if isinstance(record, dict) else {}


def _format_jcl_record_brief(item: dict[str, Any]) -> str:
    record = _selected_jcl_record(item)
    season = str(record.get("season") or "").strip()
    return season or "未标注"


def _format_jcl_record_detail_lines(item: dict[str, Any]) -> list[str]:
    record = _selected_jcl_record(item)
    season = str(record.get("season") or "").strip()
    recorded_at = str(record.get("recorded_at") or "").strip()
    note = str(record.get("note") or "").strip()

    lines = [f"JCL记录：【{season or '未标注'}】"]
    if recorded_at:
        lines.append(f"记录时间：{recorded_at}")
    if note:
        lines.append(f"JCL备注：{note}")
    return lines


def _find_supported_kungfu(kungfus: list[dict[str, Any]], kungfu_id: int) -> dict[str, Any] | None:
    for item in kungfus:
        if int(item.get("kungfu_id", 0)) == kungfu_id:
            return item
        if kungfu_id in [int(mobile_id) for mobile_id in item.get("mobile_ids") or []]:
            return item
    return None


async def get_equipment_rating_support_status(kungfu_id: int) -> bool | None:
    data = await _fetch_supported_equipment_rating_data(timeout=2)
    if isinstance(data, str):
        return None
    kungfus = data.get("kungfus") or []
    return _find_supported_kungfu(kungfus, kungfu_id) is not None


async def is_equipment_rating_supported_kungfu(kungfu_id: int) -> bool:
    return await get_equipment_rating_support_status(kungfu_id) is True


def _supported_kungfu_sort_key(item: dict[str, Any]) -> int:
    try:
        return int(item.get("kungfu_id") or 0)
    except (TypeError, ValueError):
        return 0


def _season_group_sort_key(group: tuple[str, list[dict[str, Any]]]) -> tuple[int, int]:
    season, items = group
    current_season = ""
    for item in items:
        record = _selected_jcl_record(item)
        current_season = str(record.get("current_season") or "").strip()
        if current_season:
            break
    min_kungfu_id = min(_supported_kungfu_sort_key(item) for item in items)
    return (0 if season == current_season else 1, min_kungfu_id)


def _format_supported_kungfu_list(data: dict[str, Any]) -> str:
    kungfus = data.get("kungfus") or []
    if not kungfus:
        return "当前 calculator 没有可用的装备评级心法。"
    season_groups: dict[str, list[dict[str, Any]]] = {}
    for item in sorted(kungfus, key=_supported_kungfu_sort_key):
        season = _format_jcl_record_brief(item)
        season_groups.setdefault(season, []).append(item)

    lines = [f"当前装备评级支持 {len(kungfus)} 个心法："]
    for season, items in sorted(season_groups.items(), key=_season_group_sort_key):
        lines.append(f"【{season}】")
        school_groups: dict[str, list[dict[str, Any]]] = {}
        for item in items:
            school_groups.setdefault(_supported_kungfu_school(item), []).append(item)
        for school, school_items in sorted(
            school_groups.items(),
            key=lambda group: min(_supported_kungfu_sort_key(item) for item in group[1]),
        ):
            names = "、".join(
                _supported_kungfu_name(item)
                for item in sorted(school_items, key=_supported_kungfu_sort_key)
            )
            lines.append(f"{school}：{names}")
    lines.append("查询单个心法：装备评级支持 <心法名>")
    lines.append("装备评级使用示例：装备评级 剑胆琴心 倦收天 剑纯")
    return "\n".join(lines)


def _format_supported_kungfu_detail(item: dict[str, Any]) -> str:
    selected = item.get("selected") or {}
    lines = [
        f"装备评级支持：{_supported_kungfu_school(item)}·{_supported_kungfu_name(item)}",
        f"默认评级循环：{_selected_rating_loop_text(item)}",
        *_format_jcl_record_detail_lines(item),
        f"可用评级JCL：{item.get('jcl_count', 0)} 个",
        "公共JCL选择：装备评级 <服务器> <角色> <心法> 评级列表",
    ]
    if item.get("warning"):
        lines.append(f"提示：{item['warning']}")
    return "\n".join(lines)


async def _fetch_public_rating_loops(kungfu_id: int) -> list[str] | str:
    try:
        response = await Request(
            f"{Config.jx3.api.calculator_url}/loops",
            params={"kungfu_id": kungfu_id},
        ).get(timeout=8)
        if response.status_code >= 400:
            return f"装备评级循环列表查询失败：calculator 返回 HTTP {response.status_code}。"
        result = response.json()
    except Exception as exc:
        return f"装备评级循环列表查询失败：{exc}"
    if result.get("code") == 404:
        return "该心法当前没有可用公共 JCL，默认装备评级仍可使用评级专用 JCL。"
    if result.get("code") != 200:
        return result.get("msg", "装备评级循环列表查询失败。")

    loops = []
    for item in result.get("data") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        if name:
            loops.append(name)
    if not loops:
        return "该心法当前没有可用公共 JCL，默认装备评级仍可使用评级专用 JCL。"
    return loops


def _format_public_rating_loop_list(loops: list[str]) -> str:
    lines = ["请选择装备评级循环，选择后会开始计算（顺序与计算器循环列表一致）："]
    for index, loop_name in enumerate(loops, start=1):
        lines.append(f"{index}. {loop_name}")
    return "\n".join(lines)


def _percent_from_rating(value: Any, divisor: float, base: float = 0) -> str:
    return _format_percent((_to_float(value) / divisor + base) * 100)


def _haste_level(value: Any) -> int:
    haste = _to_float(value)
    if haste < 206:
        return 0
    if haste < 9232:
        return 1
    if haste < 19285:
        return 2
    if haste < 30158:
        return 3
    if haste < 42057:
        return 4
    return 5


def _grade_icon(grade: Any) -> str:
    return _asset_uri("image", "jx3", "equipment_rating", RANK_ICON_FILES.get(str(grade), "rank_d.png"))


def _grade_theme(grade: Any) -> dict[str, str]:
    return RANK_THEMES.get(str(grade), RANK_THEMES["D"]).copy()


def _rating_avatar() -> str:
    return _asset_uri("image", "jx3", "equipment_rating", "Inkar.jpg")


def _attr_text(attributes: Any) -> str:
    if isinstance(attributes, list):
        return " ".join(
            [
                _short_attribute_text(item)
                for item in attributes
                if not _is_hidden_attribute_text(item)
            ]
        )
    if isinstance(attributes, str):
        return " ".join(
            [
                _short_attribute_text(part)
                for part in attributes.split()
                if not _is_hidden_attribute_text(part)
            ]
        )
    return ""


def _equip_icon(detail: dict[str, Any]) -> str:
    try:
        icon_id, _ = TabCache.get_icon_for_equip(int(detail.get("ui_id", 0)))
    except Exception:
        icon_id = 1434
    return f"https://icon.jx3box.com/icon/{icon_id}.png"


def _quality_class(detail: dict[str, Any]) -> str:
    if _to_float(detail.get("quality")) >= 5:
        return "quality5"
    return "quality4"


def _decoration_attribute_text(item: dict[str, Any]) -> str:
    attribute_key = str(item.get("attribute_key") or "").strip()
    label = get_attr_name(attribute_key)
    if not label:
        return ""
    return f"{label}+{_format_plain_int(item.get('value'))}"


def _decoration_chips(detail: dict[str, Any]) -> list[dict[str, str]]:
    chips = []
    for embedding in detail.get("embedding") or []:
        if not isinstance(embedding, dict):
            continue
        text = _decoration_attribute_text(embedding)
        if not text:
            continue
        level = _format_plain_int(embedding.get("level"))
        chips.append(
            {
                "icon": _asset_uri("image", "jx3", "attributes", "wuxingshi", f"{level}.png"),
                "text": text,
            }
        )
    for enchant in detail.get("enchants") or []:
        if not isinstance(enchant, dict):
            continue
        text = str(enchant.get("text") or enchant.get("name") or "").strip()
        if not text:
            continue
        icon_kind = str(enchant.get("icon_kind") or enchant.get("kind") or "")
        icon_file = "common_enchant.png" if icon_kind == "common" else "permanent_enchant.png"
        chips.append(
            {
                "icon": _asset_uri("image", "jx3", "attributes", icon_file),
                "text": text,
            }
        )
    color_stone = detail.get("color_stone")
    if isinstance(color_stone, dict):
        text = str(color_stone.get("text") or color_stone.get("name") or "").strip()
        if text:
            chips.append(
                {
                    "icon": str(color_stone.get("icon_url") or _asset_uri("image", "jx3", "attributes", "unknown.png")),
                    "text": text,
                }
            )
    return chips


def _best_equipment_text(best: dict[str, Any]) -> str:
    name = str(best.get("name") or "候选装备")
    details = []
    if _to_float(best.get("level")) > 0:
        details.append(_format_plain_int(best.get("level")))
    attribute_text = _attr_text(best.get("attribute"))
    if attribute_text:
        details.append(attribute_text)
    return f"{name}（{' '.join(details)}）" if details else name


def _prepare_slots(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prepared = []
    order = {location: index for index, location in enumerate(SLOT_DISPLAY_ORDER)}
    for slot in sorted(slots, key=lambda item: order.get(int(item.get("location_code", 99)), 99)):
        rating = slot.get("rating")
        current = slot.get("current") or {}
        best = slot.get("best") or {}
        raw_location_name = slot.get("location_name")
        location_name = SLOT_NAME_OVERRIDES.get(str(raw_location_name or ""), raw_location_name or "")
        row = {
            **slot,
            "location_name": location_name,
            "current": {
                **current,
                "icon": _equip_icon(current),
                "level_text": _format_plain_int(current.get("level")),
                "attribute_text": _attr_text(current.get("attribute")),
                "quality_class": _quality_class(current),
                "decoration_chips": _decoration_chips(current),
            },
            "best": {
                **best,
                "icon": _equip_icon(best),
                "level_text": _format_plain_int(best.get("level")),
                "attribute_text": _attr_text(best.get("attribute")),
                "quality_class": _quality_class(best),
                "decoration_chips": _decoration_chips(best),
            },
            "is_rated": rating is not None,
            "grade_icon": "",
            "score_text": "--",
            "score_value": 0,
            "best_note": "",
            "has_haste_adjustment": False,
            "upgrade_value": 0,
        }
        if rating is not None:
            grade = str(rating.get("grade", "D"))
            best_diff = _to_float(best.get("dps")) - _to_float(rating.get("current_dps"))
            adjustment = slot.get("haste_adjustment") or {}
            row.update(
                {
                    "grade_icon": _grade_icon(grade),
                    "score_text": str(rating.get("display_score", 0)),
                    "score_value": _to_float(rating.get("display_score")),
                    "best_note": f"最优 {_best_equipment_text(best)}: {_format_signed(best_diff)}",
                    "has_haste_adjustment": bool(adjustment.get("applied")),
                    "upgrade_value": best_diff,
                }
            )
        prepared.append(row)
    return prepared


def _prepare_header_summary(summary: dict[str, Any], slots: list[dict[str, Any]]) -> dict[str, Any]:
    priority_slots = []
    for slot in slots:
        if not slot.get("is_rated"):
            continue
        priority_slots.append(
            {
                "name": str(slot.get("location_name") or "").strip(),
                "score": _to_float(slot.get("score_value"), 100),
                "upgrade": _to_float(slot.get("upgrade_value")),
            }
        )
    if any(item["upgrade"] > 0.01 for item in priority_slots):
        priority_slots = [item for item in priority_slots if item["upgrade"] > 0.01]
        priority_slots.sort(key=lambda item: (-item["upgrade"], item["score"]))
    else:
        priority_slots.sort(key=lambda item: item["score"])
    names = []
    for item in priority_slots:
        if item["name"] and item["name"] not in names:
            names.append(item["name"])
        if len(names) >= 3:
            break
    return {
        "priority_tags": names or ["暂无明显短板"],
        "priority_text": " / ".join(names) if names else "暂无明显短板",
    }


def _prepare_attributes(
    summary: dict[str, Any],
    kungfu: Kungfu,
    rating_equip: JX3PlayerAttribute | None = None,
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    attributes = summary.get("attributes") or {}
    main_attr_key = attributes.get("MainAttrKey", "")
    main_attr_label = MAIN_ATTR_LABELS.get(main_attr_key, "主属性")
    role_info = [
        {"label": "门派", "value": kungfu.school or "-"},
        {"label": "心法", "value": kungfu.name or "-"},
        {"label": "主属性", "value": main_attr_label},
        {"label": "目标", "value": "134级木桩"},
    ]
    if rating_equip is not None:
        try:
            display_attrs = rating_equip.attributes
        except Exception:
            display_attrs = {}
        if display_attrs:
            basic_display_attrs, detail_display_attrs = split_display_attributes(display_attrs, kungfu.abbr)
            basic_attrs = [
                _prepare_display_attribute_row(name, value)
                for name, value in basic_display_attrs.items()
            ]
            detail_attrs = [
                _prepare_display_attribute_row(name, value)
                for name, value in detail_display_attrs.items()
                if str(name) not in HIDDEN_DETAIL_ATTRIBUTE_LABELS
            ]
            return role_info, basic_attrs, detail_attrs
    basic_attrs = [
        {"label": "装分", "value": _format_number(summary.get("current_score"))},
        {"label": "基础攻击", "value": _format_number(attributes.get("BaseAttack"))},
        {"label": "面板攻击", "value": _format_number(attributes.get("FinalAttack"))},
        {"label": main_attr_label, "value": _format_number(attributes.get("MainAttrValue"))},
    ]
    detail_attrs = [
        {"label": "会心", "value": _percent_from_rating(attributes.get("Critical"), CRITICAL_DIVISOR)},
        {"label": "会效", "value": _percent_from_rating(attributes.get("CriticalDamage"), CRITICAL_DAMAGE_DIVISOR, 1.75)},
        {"label": "破防", "value": _percent_from_rating(attributes.get("Overcome"), OVERCOME_DIVISOR)},
        {"label": "无双", "value": _percent_from_rating(attributes.get("Strain"), STRAIN_DIVISOR)},
        {"label": "破招", "value": _format_number(attributes.get("Surplus"))},
        {"label": "加速", "value": _format_haste(attributes.get("Haste"))},
    ]
    return role_info, basic_attrs, detail_attrs


def _prepare_display_attribute_row(name: Any, value: Any) -> dict[str, str]:
    label = str(name)
    if label == "加速":
        return {"label": label, "value": _format_haste(value)}
    return {"label": label, "value": str(value)}


def _prepare_attribute_incomes(summary: dict[str, Any]) -> list[dict[str, Any]]:
    raw_items = [item for item in summary.get("attribute_incomes") or [] if isinstance(item, dict)]
    attributes = summary.get("attributes") or {}
    kungfu_type = str(attributes.get("kungfu_type") or "")
    expected_keys = ATTRIBUTE_INCOME_DISPLAY_KEYS.get(kungfu_type, ())
    expected_key_set = set(expected_keys)

    incomes = []
    for item in raw_items:
        attribute_key = str(item.get("attribute_key") or "")
        if expected_key_set and attribute_key not in expected_key_set:
            continue
        if "dps_per_enchant" not in item:
            continue
        value = _to_float(item.get("dps_per_enchant"))
        label = get_attr_name(attribute_key) or str(item.get("name") or item.get("key") or "").strip()
        if not label:
            continue
        incomes.append(
            {
                "label": label,
                "value": value,
                "value_text": _format_signed_float(value),
            }
        )
    if not incomes:
        return []
    incomes.sort(key=lambda item: item["value"], reverse=True)
    max_value = max(abs(item["value"]) for item in incomes) or 1
    for item in incomes:
        item["percent"] = f"{max(4, abs(item['value']) / max_value * 100):.1f}"
    incomes[0]["is_top"] = True
    return incomes


def _prepare_distribution_view(kungfu_id: Any) -> dict[str, str] | None:
    payload = _load_equipment_rating_distribution()
    items = payload.get("items") or {}
    if not isinstance(items, dict):
        return None
    item = items.get(str(kungfu_id))
    if not isinstance(item, dict):
        return None
    image = str(item.get("image") or "").strip()
    if not image:
        return None
    return {
        "name": str(item.get("name") or "当前心法"),
        "image": _asset_uri("image", "jx3", "equipment_rating", *image.split("/")),
        "caption": "2026年5月21日统计数据",
    }


def _prepare_talents(talents: Any) -> list[dict[str, str]]:
    prepared = []
    for talent_id in talents or []:
        try:
            talent = Talent(int(talent_id))
        except Exception:
            continue
        prepared.append({"name": talent.name, "icon": talent.icon})
    return prepared


async def render_equipment_rating_image(
    data: dict[str, Any],
    role_name: str,
    server_name: str,
    rating_equip: JX3PlayerAttribute | None = None,
):
    meta = data["meta"]
    summary = data["summary"]
    kungfu = Kungfu.with_internel_id(meta["kungfu_id"])
    theme_color = kungfu.color if kungfu.name else "#4f6f87"
    role_info, basic_attrs, detail_attrs = _prepare_attributes(summary, kungfu, rating_equip)
    battle_time = _to_float(summary.get("battle_time"))
    haste_level = _haste_level(summary.get("current_haste"))
    summary_view = {
        **summary,
        "current_score_text": _format_number(summary.get("current_score")),
        "total_score_text": summary.get("display_total_score_text", f"{summary.get('display_total_score', 0):.1f}"),
        "grade_icon": _grade_icon(summary.get("grade", "D")),
        "grade_theme": _grade_theme(summary.get("grade", "D")),
        "battle_time_text": f"{battle_time:.1f}秒",
        "haste_level_text": f"{haste_level}段",
    }
    slots = _prepare_slots(data["slots"])
    chips = [
        meta.get("loop_name", "评级专用循环"),
        f"{meta.get('jcl', {}).get('weapon', '')}{meta.get('jcl', {}).get('haste', '')}",
        meta.get("income_name", "默认增益"),
        summary_view["haste_level_text"],
        summary_view["battle_time_text"],
    ]
    html = Template(
        read(build_path(TEMPLATES, ["jx3", "equipment_rating.html"]))
    ).render(
        font=Path(build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"])).as_uri(),
        theme_color=theme_color,
        role_name=role_name or "未命名配装",
        server_name=server_name,
        kungfu_name=kungfu.name or "未知心法",
        kungfu_icon=Path(kungfu.icon).as_uri(),
        meta=meta,
        summary=summary_view,
        header_avatar=_rating_avatar(),
        header_summary={
            **_prepare_header_summary(summary_view, slots),
            "title": f"{kungfu.name}体检报告" if kungfu.name else "体检报告",
        },
        role_info=role_info,
        basic_attrs=basic_attrs,
        detail_attrs=detail_attrs,
        attribute_incomes=_prepare_attribute_incomes(summary),
        distribution=_prepare_distribution_view(meta.get("kungfu_id")),
        slots=slots,
        talents=_prepare_talents(summary.get("talents")),
        warnings=data.get("warnings", []),
        chips=[chip for chip in chips if chip],
    )
    return await generate(
        html,
        ".rating-canvas",
        segment=True,
        wait_for_network=True,
        viewport={"width": 1220, "height": 1800},
    )


async def finish_equipment_rating_response(matcher: Matcher, image: Any):
    try:
        await matcher.finish(image)
    except ActionFailed as exc:
        logger.warning(f"装备评级结果发送失败，已尝试文本降级：{exc}")
        try:
            await matcher.finish(EQUIPMENT_RATING_IMAGE_SEND_FAILED)
        except ActionFailed as fallback_exc:
            logger.error(f"装备评级文本降级发送仍失败：{fallback_exc}")


async def _send_equipment_rating_started(matcher: Matcher):
    try:
        await matcher.send(EQUIPMENT_RATING_STARTED)
    except ActionFailed as exc:
        logger.warning(f"装备评级开始提示发送失败，继续计算：{exc}")


async def _resolve_equipment_rating_target(
    event: GroupMessageEvent,
    matcher: Matcher,
    server_arg: str,
    kungfu_arg: str,
) -> tuple[str, int]:
    server = Server(server_arg, event.group_id).server
    kungfu_id = Kungfu(kungfu_arg).id
    if server is None:
        await matcher.finish(PROMPT.ServerNotExist)
    if kungfu_id is None:
        await matcher.finish(PROMPT.KungfuNotExist)
    return server, int(kungfu_id)


async def _resolve_equipment_rating_player(
    matcher: Matcher,
    server: str,
    role_id: str,
):
    player_data = await search_player(role_name=role_id, role_id=role_id, server_name=server, local_lookup=True)
    if player_data.roleId == "":
        player_data = await get_uid_data(role_id=role_id, server=server, msg=False)
    if player_data.roleId == "":
        await matcher.finish(PROMPT.PlayerNotExist)
    await JX3PlayerAttribute.from_tuilan(player_data.roleId, player_data.serverName, player_data.globalRoleId)
    return player_data


async def _special_pve_kungfu_options(global_role_id: int) -> list[dict[str, Any]]:
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
                "kungfu_id": kungfu_id,
                "name": kungfu.name or str(kungfu_id),
            }
        )
    return options


def _format_special_pve_kungfu_selection(options: list[dict[str, Any]]) -> str:
    msg = "检测到该玩家有多个可用于装备评级的 PVE 心法装备，请先选择心法："
    for index, option in enumerate(options, start=1):
        msg += f"\n{index}. {option['name']}"
    return msg


def _equipment_rating_pve_tag(kungfu_id: int) -> str:
    if kungfu_id in SPECIAL_PVE_KUNGFU_TAGS:
        return SPECIAL_PVE_KUNGFU_TAGS[kungfu_id]
    abbr = Kungfu.with_internel_id(kungfu_id).abbr
    if abbr == "T":
        return "TPVE"
    if abbr == "N":
        return "HPSPVE"
    return "DPSPVE"


async def _build_equipment_rating_payload(
    event: GroupMessageEvent,
    matcher: Matcher,
    server_arg: str,
    role_id: str,
    kungfu_arg: str,
):
    server, kungfu_id = await _resolve_equipment_rating_target(event, matcher, server_arg, kungfu_arg)
    return await _build_equipment_rating_payload_by_kungfu(matcher, server, role_id, kungfu_id)


async def _build_equipment_rating_payload_by_kungfu(
    matcher: Matcher,
    server: str,
    role_id: str,
    kungfu_id: int,
):
    player_data = await _resolve_equipment_rating_player(matcher, server, role_id)
    pve_tag = _equipment_rating_pve_tag(kungfu_id)
    pve_equips = await JX3PlayerAttribute.from_database(int(player_data.globalRoleId), pve_tag, all=True)
    if pve_equips is None:
        await matcher.finish(PROMPT.EquipNotFound)
    target_equip = next(
        (
            equip
            for equip in pve_equips
            if equip.kungfu_id == kungfu_id and equip.tag == "PVE"
        ),
        None,
    )
    if target_equip is None:
        await matcher.finish("未找到该心法对应的 PVE 装备，请先提交或查询该心法 PVE 装备后重试。")

    payload = {
        "kungfu_id": int(kungfu_id),
        "jcl_data": normalize_calculator_jcl_data(target_equip.equip_lines),
        "role": {
            "name": player_data.roleName,
            "server": player_data.serverName,
            "global_role_id": int(player_data.globalRoleId),
        },
        "candidate_level": {
            "min": 32500,
            "max": 43000,
        },
    }
    return payload, player_data, target_equip


async def _request_equipment_rating_data(payload: dict[str, Any]) -> dict[str, Any] | str:
    try:
        response = await Request(f"{Config.jx3.api.calculator_url}/equipment_rating", params=payload).post(timeout=300)
        result = response.json()
    except Exception as exc:
        return f"装备评级计算失败：{exc}"

    if result.get("code") != 200:
        return result.get("msg", "装备评级计算失败。")
    data = result.get("data")
    if not isinstance(data, dict):
        return "装备评级计算失败：calculator 返回数据为空。"
    return data


async def _finish_equipment_rating_calculation(
    matcher: Matcher,
    payload: dict[str, Any],
    role_name: str,
    server_name: str,
    rating_equip: JX3PlayerAttribute,
):
    data = await _request_equipment_rating_data(payload)
    if isinstance(data, str):
        await matcher.finish(data)
    await finish_equipment_rating_response(
        matcher,
        await render_equipment_rating_image(data, role_name, server_name, rating_equip)
    )


async def handle_equipment_rating_support(matcher: Matcher, args: Message):
    query = args.extract_plain_text().strip()
    if len(query.split()) > 1:
        await matcher.finish("参考格式：装备评级支持\n参考格式：装备评级支持 <心法名>")
    data = await _fetch_supported_equipment_rating_data()
    if isinstance(data, str):
        await matcher.finish(data)
    kungfus = data.get("kungfus") or []
    if query == "":
        await matcher.finish(_format_supported_kungfu_list(data))
    if query.isdigit():
        kungfu_id = int(query)
    else:
        kungfu_id = Kungfu(query).id or 0
    if kungfu_id == 0:
        await matcher.finish(PROMPT.KungfuNotExist)
    item = _find_supported_kungfu(kungfus, kungfu_id)
    if item is None:
        kungfu = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True)
        kungfu_name = kungfu.name or "该心法"
        await matcher.finish(f"当前装备评级暂不支持 {kungfu_name}。")
    await matcher.finish(_format_supported_kungfu_detail(item))


async def handle_equipment_rating(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message):
    plain_text = args.extract_plain_text().strip()
    if plain_text == "":
        matcher.stop_propagation()
        await matcher.finish(await _render_equipment_rating_help_image())
    if plain_text.lower() in EQUIPMENT_RATING_HELP_KEYWORDS:
        await matcher.finish(await _render_equipment_rating_help_image())
    arg = plain_text.split()
    if len(arg) not in [2, 3, 4]:
        await matcher.finish(PROMPT.ArgumentCountInvalid + "\n" + EQUIPMENT_RATING_USAGE)
    use_public_loop_list = False
    if arg[-1] in RATING_LOOP_LIST_KEYWORDS:
        use_public_loop_list = True
        arg = arg[:-1]
    if len(arg) not in [2, 3]:
        await matcher.finish("评级列表参数仅支持放在命令末尾，用于选择公共 JCL。\n" + EQUIPMENT_RATING_USAGE)

    server = Server(arg[0], event.group_id).server
    if server is None:
        await matcher.finish(PROMPT.ServerNotExist)

    if len(arg) == 2:
        player_data = await _resolve_equipment_rating_player(matcher, server, arg[1])
        options = await _special_pve_kungfu_options(int(player_data.globalRoleId))
        if len(options) == 0:
            await matcher.finish("未指定心法，且未找到该玩家可用于自动选择的 PVE 心法装备，请使用：装备评级 <服务器> <角色名> <心法>")
        if len(options) > 1:
            state["equipment_rating_kungfu_options"] = options
            state["equipment_rating_server"] = server
            state["equipment_rating_role_arg"] = arg[1]
            state["equipment_rating_use_public_loop_list"] = use_public_loop_list
            await matcher.send(_format_special_pve_kungfu_selection(options))
            return
        kungfu_id = int(options[0]["kungfu_id"])
    else:
        kungfu_id = Kungfu(arg[2]).id
        if kungfu_id is None:
            await matcher.finish(PROMPT.KungfuNotExist)

    if use_public_loop_list:
        loops = await _fetch_public_rating_loops(kungfu_id)
        if isinstance(loops, str):
            await matcher.finish(loops)
        state["equipment_rating_server"] = server
        state["equipment_rating_role_arg"] = arg[1]
        state["equipment_rating_kungfu_id"] = kungfu_id
        state["equipment_rating_loops"] = loops
        await matcher.send(_format_public_rating_loop_list(loops))
        return

    await _send_equipment_rating_started(matcher)
    payload, player_data, rating_equip = await _build_equipment_rating_payload_by_kungfu(matcher, server, arg[1], kungfu_id)
    await _finish_equipment_rating_calculation(
        matcher,
        payload,
        player_data.roleName,
        player_data.serverName,
        rating_equip,
    )


async def handle_equipment_rating_loop_order(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    loop_order: Message,
):
    _ = event
    num = loop_order.extract_plain_text().strip()
    if not num.isdigit():
        await matcher.finish("循环选择有误，请重新发起命令！")
    if "equipment_rating_kungfu_options" in state:
        options = state.get("equipment_rating_kungfu_options")
        server = state.get("equipment_rating_server")
        role_arg = state.get("equipment_rating_role_arg")
        use_public_loop_list = bool(state.get("equipment_rating_use_public_loop_list"))
        if not isinstance(options, list) or not isinstance(server, str) or not isinstance(role_arg, str):
            await matcher.finish("装备评级会话已失效，请重新发起命令。")
        index = int(num)
        if index < 1 or index > len(options):
            await matcher.finish("超出可选范围，请重新发起命令！")
        kungfu_id = int(options[index - 1]["kungfu_id"])
        state.pop("equipment_rating_kungfu_options", None)
        state.pop("equipment_rating_use_public_loop_list", None)
        state.pop("rating_jcl_order", None)

        if use_public_loop_list:
            loops = await _fetch_public_rating_loops(kungfu_id)
            if isinstance(loops, str):
                await matcher.finish(loops)
            state["equipment_rating_kungfu_id"] = kungfu_id
            state["equipment_rating_loops"] = loops
            await matcher.send(_format_public_rating_loop_list(loops))
            await matcher.reject()

        await _send_equipment_rating_started(matcher)
        payload, player_data, rating_equip = await _build_equipment_rating_payload_by_kungfu(
            matcher,
            server,
            role_arg,
            kungfu_id,
        )
        await _finish_equipment_rating_calculation(
            matcher,
            payload,
            player_data.roleName,
            player_data.serverName,
            rating_equip,
        )

    loops = state.get("equipment_rating_loops")
    server = state.get("equipment_rating_server")
    role_arg = state.get("equipment_rating_role_arg")
    kungfu_id = state.get("equipment_rating_kungfu_id")
    if (
        not isinstance(loops, list)
        or not isinstance(server, str)
        or not isinstance(role_arg, str)
        or not isinstance(kungfu_id, int)
    ):
        await matcher.finish("装备评级会话已失效，请重新发起命令。")
    index = int(num)
    if index < 1 or index > len(loops):
        await matcher.finish("超出可选范围，请重新发起命令！")
    await _send_equipment_rating_started(matcher)
    payload, player_data, rating_equip = await _build_equipment_rating_payload_by_kungfu(matcher, server, role_arg, kungfu_id)
    payload = {**payload, "jcl_index": index}
    await _finish_equipment_rating_calculation(
        matcher,
        payload,
        player_data.roleName,
        player_data.serverName,
        rating_equip,
    )
