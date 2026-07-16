from __future__ import annotations

import json
import math
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
from src.utils.database import rank_db
from src.utils.database.classes import EquipmentRatingDpsRank
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
from src.utils.time import Time
from src.plugins.preferences.app import Preference

from .base import normalize_calculator_jcl_data
from .jx3box import JX3BOXCalculator
from .loop_selection import (
    calculator_loop_entries as _calculator_loop_entries,
    format_calculator_loop_selection,
)
from .timeline_render import _chart_svg, _format_compact_number
from .universe import UniversalCalculator


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
ADAPTIVE_FORMATION_RANK_GRADES = {1: "ACE", 2: "S+", 3: "S"}
EQUIPMENT_RATING_IMAGE_SEND_FAILED = (
    "装备评级图片已生成，但 QQ/NapCat 拒绝了图片上传。\n"
    "建议重启 NapCat。"
)
EQUIPMENT_RATING_STARTED = "装备评级中，请稍等片刻！"
EQUIPMENT_RATING_TIMELINE_BIN_SIZE = 1.5
EQUIPMENT_RATING_TIMELINE_ROLLING_WINDOW = 10
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
    "2. 再执行评级：装备评级 <服务器> <角色名/ID> [心法] [评级列表]\n"
    "   或：装备评级 <魔盒配装ID> [评级列表]\n"
    "   例如：装备评级 剑胆琴心 倦收天 太虚剑意\n"
    "3. 查看目前支持心法：装备评级支持 或 装备评级支持 <心法名>\n"
    "帮助：装备评级 help"
)
EQUIPMENT_RATING_HELP_KEYWORDS = {"help", "帮助", "？", "?"}
EQUIPMENT_RATING_DISTRIBUTION_PATH = build_path(
    ASSETS, ["source", "jx3", "equipment_rating_distribution.json"]
)
ADAPTIVE_ICON_ITEM_NAME_BY_CODE = {
    "BLSZY": "百炼水煮鱼",
    "FY_ATTACK_INGOT_PHYSICS": "风语·瀑沙熔锭（外攻）",
    "FY_ATTACK_INGOT_MAGIC": "风语·坠宵熔锭（内攻）",
    "FY_THERAPY_INGOT": "风语·絮泊熔锭（疗伤）",
    "HOME_WINE_FEN_THIRTEEN_DAYS": "汾酒·旬又三",
    "HOME_WINE_GUANWAI_THIRTEEN_DAYS": "关外白酒·旬又三",
    "HOME_WINE_GAOLIANG_THIRTEEN_DAYS": "高粱酒·旬又三",
    "HOME_WINE_ZHUANGYUAN_THIRTEEN_DAYS": "状元红·旬又三",
    "HOME_WINE_NUERHONG_THIRTEEN_DAYS": "女儿红·旬又三",
    "XUFENG_NINGWEI_QIUSHUANG": "煦风·宁为秋霜",
    "XUFENG_YANYAN_YUFEI": "煦风·燕燕于飞",
    "CREATIVE_FOOD_SHENG_LIFE_DOWN_STRAIN": "创意食品·盛",
    "CREATIVE_FOOD_SHENG_LIFE_DOWN_MAGIC_ATTACK": "创意食品·盛",
    "CREATIVE_FOOD_SHENG_LIFE_DOWN_PHYSICS_ATTACK": "创意食品·盛",
    "CREATIVE_FOOD_SHENG_LIFE_DOWN_OVERCOME": "创意食品·盛",
    "CREATIVE_FOOD_SHENG_LIFE_DOWN_CRITICAL": "创意食品·盛",
}
ADAPTIVE_FORMATION_ALIASES = {
    "龙皇雪风阵": "凌雪阵",
    "千机百变阵": "天罗阵",
    "苍梧引灵阵": "万灵阵",
    "九宫八卦阵": "气纯阵",
    "万籁金弦阵": "莫问阵",
    "墟海引归阵": "蓬莱阵",
    "北斗七星阵": "剑纯阵",
    "七绝逍遥阵": "花间阵",
    "天鼓雷音阵": "易筋阵",
    "万蛊噬心阵": "毒经阵",
    "横云破锋阵": "刀宗阵",
    "九音惊弦阵": "冰心阵",
    "江湖行侠阵": "通用阵",
}
ADAPTIVE_FORMATION_FALLBACK_ICON_IDS = {
    "江湖行侠阵": 22210,
}
ADAPTIVE_DISPLAY_GROUPS = [
    ("food", "食品类", {"辅助食品", "增强食品"}),
    ("medicine", "药品类", {"辅助药品", "增强药品"}),
    ("home", "家园类（酒 / 创意料理）", {"家园酒", "创意料理·盛"}),
    ("ingot", "熔锭", {"熔锭"}),
]


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
.examples {
  margin-top: 9px;
  display: grid;
  gap: 7px;
  font-size: 16px;
  line-height: 1.45;
  color: #5a6473;
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
    <div class="subtitle">输出与防御心法会在同一条评级 JCL、同一套默认评级增益下比较当前部位、空槽样本和候选装备；奶妈心法使用承压模型，以目标破产概率下的最大每秒承伤作为评分指标。</div>
  </div>

  <div class="section">
    <div class="section-title">使用步骤</div>
    <div class="steps">
      <div class="step"><div class="num">1</div><div>先提交属性：<span class="command">提交属性 &lt;服务器&gt; &lt;角色名&gt; &lt;心法&gt; &lt;茗伊装备导出码&gt;</span></div></div>
      <div class="step"><div class="num">2</div><div>再执行评级：<span class="command">装备评级 &lt;服务器&gt; &lt;角色名/ID&gt; [&lt;心法&gt;] [评级列表]</span> 或 <span class="command">装备评级 &lt;魔盒配装ID&gt; [评级列表]</span>
        <div class="examples">
          <div>角色名：<span class="command">装备评级 剑胆琴心 倦收天</span></div>
          <div>评级列表：<span class="command">装备评级 剑胆琴心 倦收天 评级列表</span></div>
          <div>魔盒配装：<span class="command">装备评级 123456 评级列表</span></div>
        </div>
      </div></div>
      <div class="step"><div class="num">3</div><div>查看支持心法：<span class="command">装备评级支持</span> 或 <span class="command">装备评级支持 &lt;心法名&gt;</span></div></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">评级依据</div>
    <div class="steps">
      <div class="step"><div class="num">A</div><div>每个部位会计算三类样本：当前装备、去掉该部位后的空槽样本、同部位候选装备。</div></div>
      <div class="step"><div class="num">B</div><div>所有样本使用同一条评级 JCL 和默认评级增益，避免把循环和增益差异混进装备评分。</div></div>
      <div class="step"><div class="num">C</div><div>“最优候选”来自当前候选池中评级指标最高的该部位装备；输出与防御心法看修正 DPS，奶妈心法看承压能力。</div></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">奶妈承压评级依据</div>
    <div class="steps">
      <div class="step"><div class="num">H</div><div>直接使用装备面板的治疗量、会心、会效和加速。不考虑装备特效，心法特性，纯静态面板计算。</div></div>
      <div class="step"><div class="num">T</div><div>高压窗口 \\(T=10\\) 秒，血量上限 \\(U=3200000\\)，目标破产概率 \\(q=5\\%\\)。伤害从 \\(t=0\\) 开始，到 \\(t=10\\) 结束，共结算 11 次。</div></div>
      <div class="step"><div class="num">G</div><div>治疗间隔 \\(\\Delta=1.5/(1+a_{\\mathrm{eff}}/210078)\\)，其中 \\(a_{\\mathrm{eff}}=\\min(a,42057)\\)。每个治疗时间点按 3 次独立治疗计算，会心按面板概率分布。</div></div>
    </div>
    <div class="formula-grid" style="margin-top: 16px;">
      <div class="formula-block">
        <div class="formula-title">血量递推</div>
        <div class="formula">\\[
R_0 = U - d
\\]
\\[
R_{i+1} = \\min(U, R_i + H_i) - d
\\]</div>
        <div class="formula-note">若任意结算后 \\(R_i < 0\\)，则视为破产。治疗 \\(H_i\\) 统计区间 \\([i,i+1)\\) 内发生的所有治疗，并先受血量上限截断。</div>
      </div>
      <div class="formula-block">
        <div class="formula-title">承压能力</div>
        <div class="formula">\\[
\\tau = \\inf\\{i : R_i < 0\\}
\\]
\\[
d^* = \\max\\{d: \\Pr(\\tau \\le T) \\le q\\}
\\]</div>
        <div class="formula-note">\\(\\tau\\) 是首次破产的整数伤害结算点。承压能力 \\(d^*\\)为每秒承伤。单件评分固定当前推荐的小药、熔锭和阵眼配置后，比较当前、空槽和候选装备的 \\(d^*\\)。</div>
      </div>
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
        viewport={"width": 980, "height": 2550},
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
    "Therapy": (
        "atTherapyPowerBase",
        "atAllTypeCriticalStrike",
        "atAllTypeCriticalDamagePowerBase",
    ),
}
TANK_VITALITY_CONVERSION_STEP = 3310
TANK_VITALITY_CONVERSION_MAX_STACKS = 100


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


def _format_signed_percent(value: Any) -> str:
    number = _to_float(value)
    if abs(number) < 0.05:
        return "+0.0%"
    return f"{number:+.1f}%"


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _trial_land_int(value: Any) -> int | None:
    number = _trial_land_float(value)
    return int(number) if number is not None else None


def _trial_land_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _trial_land_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _trial_land_item_name(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("name") or value.get("label") or value.get("code") or "").strip()
    return str(value or "").strip()


def _trial_land_item_fields(value: Any) -> tuple[str, str]:
    code = str(_as_dict(value).get("code") or "").strip()
    name = _trial_land_item_name(value)
    if not code and isinstance(value, str) and value.strip() in ADAPTIVE_ICON_ITEM_NAME_BY_CODE:
        code = value.strip()
    if code and (not name or name == code):
        name = ADAPTIVE_ICON_ITEM_NAME_BY_CODE.get(code, name or code)
    return name, code


def _trial_land_boss_name_map(bosses: Any) -> dict[str, str]:
    names: dict[str, str] = {}
    for boss in bosses if isinstance(bosses, list) else []:
        if not isinstance(boss, dict):
            continue
        boss_id = str(boss.get("id") or "").strip()
        name = str(boss.get("name") or "").strip()
        if boss_id and name:
            names[boss_id] = name
    return names


def _trial_land_boss_names(stage: Any, boss_names: dict[str, str]) -> list[str]:
    stage_data = _as_dict(stage)
    boss_ids = stage_data.get("selected_boss_ids")
    if not isinstance(boss_ids, list):
        return []
    names = []
    for boss_id in boss_ids:
        normalized_id = str(boss_id or "").strip()
        name = boss_names.get(normalized_id, "")
        if name and name not in names:
            names.append(name)
    return names


def _trial_land_selected_boss_ids(stages: Any) -> list[str]:
    selected: list[str] = []
    for stage_key in ("first", "second"):
        boss_ids = _as_dict(_as_dict(stages).get(stage_key)).get("selected_boss_ids")
        if not isinstance(boss_ids, list):
            continue
        for boss_id in boss_ids:
            normalized_id = str(boss_id or "").strip()
            if normalized_id and normalized_id not in selected:
                selected.append(normalized_id)
    return selected


def _prepare_trial_land_target(raw: Any, boss_names: dict[str, str]) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    floor = _trial_land_int(raw.get("floor"))
    required_dps = _trial_land_int(raw.get("required_dps"))
    gap_dps = _trial_land_int(raw.get("gap_dps"))
    reached = raw.get("reached")
    bottleneck_stage = str(raw.get("bottleneck_stage") or "").strip().lower()
    if (
        floor is None
        or floor <= 0
        or required_dps is None
        or required_dps < 0
        or gap_dps is None
        or gap_dps < 0
        or not isinstance(reached, bool)
        or bottleneck_stage not in {"first", "second", "both"}
    ):
        return None

    gap_percent_raw = raw.get("gap_percent")
    gap_percent = None if gap_percent_raw is None else _trial_land_float(gap_percent_raw)
    if gap_percent is not None and gap_percent < 0:
        return None
    stages = _as_dict(raw.get("stages"))
    first_bosses = _trial_land_boss_names(stages.get("first"), boss_names)[:1]
    second_bosses = _trial_land_boss_names(stages.get("second"), boss_names)[:2]
    if len(first_bosses) != 1 or len(second_bosses) != 2:
        return None

    bottleneck_text = {
        "first": "阶段一",
        "second": "阶段二",
        "both": "两个阶段",
    }[bottleneck_stage]
    return {
        "floor": floor,
        "floor_text": f"第{floor}层",
        "required_dps": required_dps,
        "required_dps_text": _format_number(required_dps),
        "gap_dps": gap_dps,
        "gap_dps_text": _format_number(gap_dps),
        "gap_percent": gap_percent,
        "gap_percent_text": f"+{gap_percent:.2f}%" if gap_percent is not None else "无法换算",
        "reached": reached,
        "status_text": "已达到" if reached else "尚有差距",
        "bottleneck_stage": bottleneck_stage,
        "bottleneck_text": bottleneck_text,
        "selected_boss_ids": _trial_land_selected_boss_ids(stages),
        "first_bosses": first_bosses,
        "second_bosses": second_bosses,
        "route_text": f"{first_bosses[0]} / {' + '.join(second_bosses)}",
    }


def _prepare_trial_land_boss_rows(
    raw: Any,
    *,
    selected_boss_ids: set[str],
    data_max_floor: int | None,
) -> list[dict[str, Any]]:
    rows = []
    for order, boss in enumerate(raw if isinstance(raw, list) else []):
        if not isinstance(boss, dict):
            continue
        boss_id = str(boss.get("id") or "").strip()
        name = str(boss.get("name") or "").strip()
        stage = _trial_land_int(boss.get("stage"))
        max_floor = _trial_land_int(boss.get("max_floor"))
        if not boss_id or not name or stage not in {1, 2} or max_floor is None or max_floor < 0:
            continue

        target_required_dps = _trial_land_int(boss.get("target_required_dps"))
        target_floor_hp = _trial_land_int(boss.get("target_floor_hp"))
        if data_max_floor is not None and data_max_floor > 0:
            progress = max_floor / data_max_floor * 100
            progress_basis = "血量表层数"
        else:
            progress = 0
            progress_basis = "层数"
        progress = round(min(100.0, max(0.0, progress)), 1)
        rows.append(
            {
                "id": boss_id,
                "name": name,
                "stage": stage,
                "stage_text": f"阶段{'一' if stage == 1 else '二'}",
                "max_floor": max_floor,
                "max_floor_text": f"{max_floor}层" if max_floor > 0 else "未通过第1层",
                "progress_percent": progress,
                "progress_percent_text": f"{progress:.1f}%",
                "progress_basis": progress_basis,
                "selected": boss_id in selected_boss_ids,
                "target_required_dps": target_required_dps,
                "target_required_dps_text": _format_number(target_required_dps) if target_required_dps is not None else "",
                "target_floor_hp": target_floor_hp,
                "target_floor_hp_text": _format_number(target_floor_hp) if target_floor_hp is not None else "",
                "_order": order,
            }
        )
    rows.sort(key=lambda item: (item["stage"], item["_order"]))
    for item in rows:
        item.pop("_order", None)
    return rows


TRIAL_LAND_ATTRIBUTE_LABELS = {
    "atPhysicsAttackPowerBase": "外攻",
    "atMagicAttackPowerBase": "内攻",
    "atPhysicsCriticalStrike": "会心",
    "atMagicCriticalStrike": "会心",
    "atPhysicsCriticalDamagePowerBase": "会效",
    "atMagicCriticalDamagePowerBase": "会效",
    "atPhysicsOvercomeBase": "破防",
    "atMagicOvercome": "破防",
    "atSurplusValueBase": "破招",
    "atStrainBase": "无双",
}


def _prepare_trial_land_attribute_incomes(raw: Any, target: dict[str, Any] | None) -> list[dict[str, Any]]:
    gap_dps = int(target["gap_dps"]) if target is not None else None
    reached = bool(target["reached"]) if target is not None else False
    incomes = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict) or str(item.get("metric_key") or "") != "raw_dps":
            continue
        attribute_key = str(item.get("attribute_key") or "").strip()
        dps_per_100 = _trial_land_float(item.get("dps_per_100"))
        dps_per_point = _trial_land_float(item.get("dps_per_point"))
        dps_per_enchant = _trial_land_float(item.get("dps_per_sample"))
        sample_value = _trial_land_int(item.get("sample_value"))
        label = TRIAL_LAND_ATTRIBUTE_LABELS.get(attribute_key) or get_attr_name(attribute_key)
        if not attribute_key or not label or sample_value is None or sample_value <= 0:
            continue
        if dps_per_point is None and dps_per_100 is not None:
            dps_per_point = dps_per_100 / 100
        if dps_per_enchant is None and dps_per_point is not None:
            dps_per_enchant = dps_per_point * sample_value
        if dps_per_enchant is None:
            continue
        if dps_per_point is None:
            dps_per_point = dps_per_enchant / sample_value
        if target is None:
            points_needed = None
            points_needed_text = "待目标数据"
        elif reached or gap_dps == 0:
            points_needed = 0
            points_needed_text = "已达标"
        elif dps_per_point > 0:
            points_needed = math.ceil(gap_dps / dps_per_point)
            points_needed_text = f"约 {_format_number(points_needed)} 点"
        else:
            points_needed = None
            points_needed_text = "无法估算"
        incomes.append(
            {
                "attribute_key": attribute_key,
                "label": label,
                "sample_value": sample_value,
                "sample_value_text": _format_number(sample_value),
                "dps_per_enchant": dps_per_enchant,
                "dps_per_enchant_text": f"{dps_per_enchant:+,.0f}",
                "value_text": f"每附魔约 {dps_per_enchant:+,.0f} DPS",
                "points_needed": points_needed,
                "points_needed_text": points_needed_text,
            }
        )
    incomes.sort(key=lambda item: item["dps_per_enchant"], reverse=True)
    max_income = max((max(0.0, item["dps_per_enchant"]) for item in incomes), default=0.0)
    for index, item in enumerate(incomes):
        bar_percent = max(0.0, item["dps_per_enchant"]) / max_income * 100 if max_income > 0 else 0.0
        item["bar_percent"] = round(bar_percent, 1)
        item["bar_width"] = f"{bar_percent:.1f}%"
        item["is_top"] = index == 0
    return incomes


def _trial_land_summary_metrics(
    *,
    max_floor_text: str,
    expected_dps: int,
    capped: bool,
    target: dict[str, Any] | None,
    wine_locked_for_haste: bool,
) -> list[dict[str, str]]:
    if target is None:
        target_metric = (
            {
                "key": "target_gap",
                "label": "数据上限",
                "value": "已达到",
                "detail": "旧 calculator 未返回目标门槛",
                "state": "ok",
            }
            if capped
            else {
                "key": "target_gap",
                "label": "下一目标",
                "value": "待计算",
                "detail": "当前 calculator 未返回目标差距",
                "state": "muted",
            }
        )
    else:
        reached = bool(target["reached"])
        target_metric = {
            "key": "target_gap",
            "label": f"到 {target['floor']} 层",
            "value": "已达到" if reached else target["gap_percent_text"],
            "detail": "无需额外DPS" if reached else f"还差 {target['gap_dps_text']} DPS",
            "state": "ok" if reached else "warning",
        }
    return [
        {
            "key": "max_floor",
            "label": "最高可通关",
            "value": max_floor_text,
            "detail": (
                "已达到血量表上限"
                if capped
                else (
                    f"{target['floor']}层目标：{target['bottleneck_text']}瓶颈"
                    if target is not None
                    else "按三首领通关规则"
                )
            ),
            "state": "ok",
        },
        {
            "key": "expected_dps",
            "label": "试炼预期DPS（133级首领）",
            "value": _format_number(expected_dps),
            "detail": "加速酒已锁定" if wine_locked_for_haste else "主属性酒已锁定",
            "state": "default",
        },
        target_metric,
    ]


def _trial_land_optimization_steps(
    target: dict[str, Any] | None,
    attribute_incomes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if target is None:
        return []
    reached = bool(target["reached"])
    positive_incomes = [item for item in attribute_incomes if item["dps_per_enchant"] > 0]
    best_income = positive_incomes[0] if positive_incomes else None
    second_income = positive_incomes[1] if len(positive_incomes) > 1 else None
    if best_income is None:
        priority_text = "暂无可靠属性优先级"
    elif second_income is None:
        priority_text = f"优先{best_income['label']}"
    else:
        priority_text = f"优先{best_income['label']}，其次{second_income['label']}"
    route_detail = f"阶段一选 {target['first_bosses'][0]}；阶段二选 {'、'.join(target['second_bosses'])}"
    if reached:
        return [
            {
                "key": "threshold",
                "index": 1,
                "title": f"维持{target['bottleneck_text']}阈值",
                "value": f"当前已满足 {target['required_dps_text']} DPS",
                "detail": route_detail,
                "state": "ok",
            },
            {
                "key": "route",
                "index": 2,
                "title": "保持锁定首领路线",
                "value": target["route_text"],
                "detail": "三个首领均按当前试炼增益计算",
                "state": "ok",
            },
            {
                "key": "attribute",
                "index": 3,
                "title": "属性无需为通关额外堆叠",
                "value": "当前试炼预期DPS已达标",
                "detail": "保持锁定增益和循环稳定性即可",
                "state": "ok",
            },
        ]

    if best_income is not None:
        attribute_value = f"{best_income['label']}{best_income['points_needed_text']}"
        if second_income is not None:
            attribute_value += f"，或{second_income['label']}{second_income['points_needed_text']}"
        attribute_detail = "按当前样本边际收益线性估算"
        attribute_state = "warning"
    else:
        attribute_value = "暂无可靠属性样本"
        attribute_detail = "建议先提升整体装分后重新评级"
        attribute_state = "muted"
    return [
        {
            "key": "threshold",
            "index": 1,
            "title": f"补齐{target['bottleneck_text']}阈值",
            "value": f"目标门槛 {target['required_dps_text']} DPS",
            "detail": route_detail,
            "state": "warning",
        },
        {
            "key": "dps_gap",
            "index": 2,
            "title": f"提高 {target['gap_dps_text']} DPS",
            "value": (
                f"相对当前约 {target['gap_percent_text']}"
                if target["gap_percent"] is not None
                else "当前DPS为 0，暂无法换算比例"
            ),
            "detail": "以试炼预期DPS为准",
            "state": "warning",
        },
        {
            "key": "attribute",
            "index": 3,
            "title": priority_text,
            "value": attribute_value,
            "detail": attribute_detail,
            "state": attribute_state,
        },
    ]


def _prepare_trial_land(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return {
            "status": "failed",
            "message": "试炼之地预估返回格式异常，已跳过展示。",
        }

    status = str(raw.get("status") or "").strip().lower().replace("-", "_").replace(" ", "_")
    if status in {"not_applicable", "not_applicable_to_role", "skipped", "disabled"}:
        return None
    if status != "ok":
        warnings = raw.get("warnings")
        warning = next(
            (str(item).strip() for item in warnings if str(item).strip()),
            "",
        ) if isinstance(warnings, list) else ""
        message = str(raw.get("message") or warning or "试炼之地预估暂不可用。").strip()
        if len(message) > 120:
            message = message[:117] + "..."
        return {
            "status": "failed",
            "message": message,
        }

    metric = str(raw.get("metric") or "").strip().lower()
    dps = _trial_land_int(raw.get("dps"))
    max_floor = _trial_land_int(raw.get("max_floor"))
    if metric != "raw_dps" or dps is None or dps < 0 or max_floor is None or max_floor < 0:
        return {
            "status": "failed",
            "message": "试炼之地预估数据不完整，已跳过展示。",
        }

    stages = _as_dict(raw.get("stages"))
    boss_names = _trial_land_boss_name_map(raw.get("bosses"))
    first_bosses = _trial_land_boss_names(stages.get("first"), boss_names)[:1]
    second_bosses = _trial_land_boss_names(stages.get("second"), boss_names)[:2]
    if len(first_bosses) != 1 or len(second_bosses) != 2:
        return {
            "status": "failed",
            "message": "试炼之地预估缺少推荐首领，已跳过展示。",
        }
    capped = _trial_land_bool(raw.get("capped"))
    max_floor_text = f"{max_floor}层" if max_floor > 0 else "未通过第1层"
    target = _prepare_trial_land_target(raw.get("target"), boss_names)
    selected_boss_ids = set(
        target["selected_boss_ids"]
        if target is not None
        else _trial_land_selected_boss_ids(stages)
    )
    data_max_floor = _trial_land_int(_as_dict(raw.get("data")).get("max_floor"))
    boss_rows = _prepare_trial_land_boss_rows(
        raw.get("bosses"),
        selected_boss_ids=selected_boss_ids,
        data_max_floor=data_max_floor,
    )
    attribute_incomes = _prepare_trial_land_attribute_incomes(raw.get("attribute_incomes"), target)
    buffs = _as_dict(raw.get("buffs"))
    wine_locked_for_haste = _trial_land_bool(_as_dict(raw.get("haste")).get("wine_locked_for_haste"))
    selected = _as_dict(buffs.get("selected"))
    consumables = []
    for key, label in (
        ("wine", "酒"),
        ("creative_food", "创意料理"),
        ("ointment", "香膏"),
    ):
        raw_item = selected.get(key)
        name, code = _trial_land_item_fields(raw_item)
        name = name or "未提供"
        consumables.append(
            {
                "key": key,
                "label": label,
                "name": name,
                "code": code,
                "group": "择优增益",
                "icon": _adaptive_icon({"name": name, "codes": [code] if code else []}),
            }
        )
    fixed_consumables = []
    for index, item in enumerate(buffs.get("fixed") if isinstance(buffs.get("fixed"), list) else []):
        name, code = _trial_land_item_fields(item)
        if not name:
            continue
        if code == "BLSZY" or "百炼水煮鱼" in name:
            base_key = "fish"
            label = "百炼水煮鱼"
            display_order = 2
        elif "INGOT" in code or "熔锭" in name:
            base_key = "ingot"
            label = "熔锭"
            display_order = 1
        else:
            base_key = f"fixed_{index + 1}"
            label = "固定增益"
            display_order = index + 3
        key = base_key
        if any(existing["key"] == key for existing in fixed_consumables):
            key = f"{base_key}_{index + 1}"
        fixed_consumables.append(
            {
                "key": key,
                "label": label,
                "name": name,
                "code": code,
                "group": "固定增益",
                "icon": _adaptive_icon({"name": name, "codes": [code] if code else []}),
                "_display_order": display_order,
            }
        )
    fixed_consumables.sort(key=lambda item: item["_display_order"])
    for item in fixed_consumables:
        item.pop("_display_order", None)
    return {
        "status": "ok",
        "max_floor": max_floor,
        "max_floor_text": max_floor_text,
        "raw_dps": dps,
        "raw_dps_text": _format_number(dps),
        "expected_dps_text": _format_number(dps),
        "capped": capped,
        "first_bosses": first_bosses,
        "second_bosses": second_bosses,
        "target_available": target is not None,
        "target": target,
        "summary_metrics": _trial_land_summary_metrics(
            max_floor_text=max_floor_text,
            expected_dps=dps,
            capped=capped,
            target=target,
            wine_locked_for_haste=wine_locked_for_haste,
        ),
        "boss_rows": boss_rows,
        "boss_rows_complete": len(boss_rows) == 9,
        "optimization_steps": _trial_land_optimization_steps(target, attribute_incomes),
        "attribute_incomes": attribute_incomes,
        "fixed_consumables": fixed_consumables,
        "consumables": consumables,
        "consumable_items": [*consumables, *fixed_consumables],
    }


def _equipment_rating_timeline_loop_payload(meta: dict[str, Any]) -> dict[str, Any] | None:
    jcl = _as_dict(meta.get("jcl"))
    weapon = str(jcl.get("weapon") or "").strip()
    haste = str(jcl.get("haste") or "").strip()
    loop_name = str(jcl.get("raw_loop") or "").strip()
    if not weapon or not haste or not loop_name:
        return None
    selected_loop = _as_dict(meta.get("jcl_loop"))
    user_id = int(_to_float(selected_loop.get("user_id")))
    payload = {
        "name": str(meta.get("loop_name") or loop_name),
        "index": 1,
        "weapon": weapon,
        "haste": haste,
        "loop": loop_name,
        "user_id": user_id,
    }
    if str(meta.get("jcl_source") or "") == "rating_jcl":
        payload["source"] = "rating_jcl"
    return payload


async def _request_equipment_rating_timeline(
    rating_data: dict[str, Any],
    rating_payload: dict[str, Any],
) -> dict[str, Any] | None:
    meta = _as_dict(rating_data.get("meta"))
    adaptive = _as_dict(rating_data.get("adaptive_consumables"))
    if adaptive.get("status") != "ok":
        return None
    full_income = [str(code) for code in adaptive.get("full_income_codes") or [] if str(code)]
    if not full_income:
        return None
    loop_payload = _equipment_rating_timeline_loop_payload(meta)
    if loop_payload is None:
        return None
    payload = {
        "kungfu_id": int(_to_float(meta.get("kungfu_id"))),
        "jcl_data": normalize_calculator_jcl_data(rating_payload.get("jcl_data") or []),
        "loops": [loop_payload],
        "full_income": full_income,
        "user_id": int(loop_payload.get("user_id") or 0),
        "bin_size": EQUIPMENT_RATING_TIMELINE_BIN_SIZE,
        "rolling_window": EQUIPMENT_RATING_TIMELINE_ROLLING_WINDOW,
        "rating_replay": True,
    }
    try:
        response = await Request(f"{Config.jx3.api.calculator_url}/damage_timeline", params=payload).post(timeout=120)
        result = response.json()
    except Exception as exc:
        logger.warning(f"装备评级循环曲线生成失败：{exc}")
        return None
    if result.get("code") != 200:
        logger.warning(f"装备评级循环曲线生成失败：{result.get('msg') or 'calculator 返回失败'}")
        return None
    data = result.get("data")
    return data if isinstance(data, dict) else None


def _prepare_rating_timeline(timeline_data: dict[str, Any] | None) -> dict[str, str] | None:
    if not isinstance(timeline_data, dict):
        return None
    series_list = [series for series in timeline_data.get("series") or [] if isinstance(series, dict)]
    if not series_list:
        return None
    bin_size = _to_float(timeline_data.get("bin_size"), EQUIPMENT_RATING_TIMELINE_BIN_SIZE)
    chart = _chart_svg(
        series_list,
        "damage_per_second_bin",
        ["#2F6BFF"],
        f"每{bin_size:g}秒伤害量" if bin_size != 1 else "每秒伤害量",
        460,
        142,
        True,
        buff_overlays=timeline_data.get("buff_overlays") or [],
        stroke_width=3,
    )
    if not chart:
        return None
    series = series_list[0]
    adjusted = _as_dict(series.get("adjusted"))
    return {
        "chart": chart,
        "loop_name": str(series.get("loop_name") or "评级循环"),
        "dps": _format_compact_number(adjusted.get("dps")),
        "total_damage": _format_compact_number(adjusted.get("total_damage")),
    }


def _equipment_rating_adaptive_dps(data: dict[str, Any]) -> int:
    adaptive = _as_dict(data.get("adaptive_consumables"))
    if adaptive.get("status") != "ok":
        return 0
    return int(_to_float(adaptive.get("dps")))


def _equipment_rating_rank_label(data: dict[str, Any]) -> str:
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
    metric = str(summary.get("metric") or meta.get("metric") or "").strip()
    if metric == "therapy_ruin_capacity":
        return "承压排名"
    return "伤害排名"


def _equipment_rating_rank_jcl_key(meta: dict[str, Any]) -> str:
    jcl = _as_dict(meta.get("jcl"))
    selected_loop = _as_dict(meta.get("jcl_loop"))
    rating_model = str(meta.get("rating_model") or "").strip()
    if rating_model == "therapy_ruin":
        payload = {
            "rating_model": rating_model,
            "model_name": str(meta.get("loop_name") or "").strip(),
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    weapon = str(jcl.get("weapon") or "").strip()
    haste = str(jcl.get("haste") or "").strip()
    loop_name = str(jcl.get("raw_loop") or jcl.get("loop") or meta.get("loop_name") or "").strip()
    if not loop_name:
        return ""
    payload = {
        "weapon": weapon,
        "haste": haste,
        "loop": loop_name,
        "source": str(meta.get("jcl_source") or selected_loop.get("source") or "").strip(),
        "user_id": int(_to_float(selected_loop.get("user_id"))),
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _equipment_rating_rank_jcl_name(meta: dict[str, Any]) -> str:
    jcl = _as_dict(meta.get("jcl"))
    weapon = str(jcl.get("weapon") or "").strip()
    haste = str(jcl.get("haste") or "").strip()
    loop_name = str(jcl.get("raw_loop") or jcl.get("loop") or meta.get("loop_name") or "").strip()
    prefix = f"{weapon}{haste}".strip()
    if prefix and loop_name:
        return f"{prefix}_{loop_name}"
    return loop_name or str(meta.get("loop_name") or "评级专用循环")


def _same_equipment_rating_role(record: EquipmentRatingDpsRank, server_name: str, role_id: str, global_role_id: int) -> bool:
    if global_role_id > 0 and int(record.global_role_id or 0) == global_role_id:
        return True
    return bool(role_id) and record.server_name == server_name and record.role_id == role_id


def _record_equipment_rating_rank(
    data: dict[str, Any],
    role_name: str,
    server_name: str,
    role_id: str,
    global_role_id: int,
) -> dict[str, Any] | None:
    meta = _as_dict(data.get("meta"))
    kungfu_id = int(_to_float(meta.get("kungfu_id")))
    dps = _equipment_rating_adaptive_dps(data)
    jcl_key = _equipment_rating_rank_jcl_key(meta)
    if kungfu_id <= 0 or dps <= 0 or not jcl_key:
        return None

    records = rank_db.where_all(
        EquipmentRatingDpsRank(),
        "kungfu_id = ? AND jcl_key = ?",
        kungfu_id,
        jcl_key,
        default=[],
    ) or []
    same_role_records = [
        record
        for record in records
        if isinstance(record, EquipmentRatingDpsRank)
        and _same_equipment_rating_role(record, server_name, role_id, global_role_id)
    ]
    current = same_role_records[0] if same_role_records else EquipmentRatingDpsRank()
    for duplicate in same_role_records[1:]:
        if duplicate.id is not None:
            rank_db.delete(EquipmentRatingDpsRank(), "id = ?", duplicate.id)

    current.role_name = role_name
    current.server_name = server_name
    current.role_id = role_id
    current.global_role_id = global_role_id
    current.kungfu_id = kungfu_id
    current.jcl_key = jcl_key
    current.jcl_name = _equipment_rating_rank_jcl_name(meta)
    current.dps = dps
    current.timestamp = Time().raw_time
    rank_db.save(current)

    ranking_records = rank_db.where_all(
        EquipmentRatingDpsRank(),
        "kungfu_id = ? AND jcl_key = ?",
        kungfu_id,
        jcl_key,
        default=[],
    ) or []
    valid_records = [
        record
        for record in ranking_records
        if isinstance(record, EquipmentRatingDpsRank) and int(record.dps or 0) > 0
    ]
    if not valid_records:
        return None
    rank = 1 + sum(1 for record in valid_records if int(record.dps or 0) > dps)
    return {
        "rank": rank,
        "total": len(valid_records),
        "text": f"{_equipment_rating_rank_label(data)} 第 {rank} / {len(valid_records)}",
    }


def record_equipment_rating_rank(
    data: dict[str, Any],
    role_name: str,
    server_name: str,
    role_id: str,
    global_role_id: int,
) -> dict[str, Any] | None:
    return _record_equipment_rating_rank(data, role_name, server_name, role_id, global_role_id)


async def _fetch_supported_equipment_rating_data(timeout: int = 8) -> dict[str, Any] | str:
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
    if item.get("rating_model") == "therapy_ruin":
        return "不需要 JCL"
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
    if item.get("rating_model") == "therapy_ruin":
        record = _selected_jcl_record(item)
        note = str(record.get("note") or "").strip()
        lines = ["评级模型：奶妈承压模型"]
        if note:
            lines.append(f"模型备注：{note}")
        return lines
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
    if item.get("rating_model") == "therapy_ruin":
        lines = [
            f"装备评级支持：{_supported_kungfu_school(item)}·{_supported_kungfu_name(item)}",
            "默认评级模型：奶妈承压模型",
            *_format_jcl_record_detail_lines(item),
            "该模型不需要评级 JCL，直接使用装备面板治疗、会心、会效和加速计算承压能力。",
        ]
        if item.get("warning"):
            lines.append(f"提示：{item['warning']}")
        return "\n".join(lines)
    lines = [
        f"装备评级支持：{_supported_kungfu_school(item)}·{_supported_kungfu_name(item)}",
        f"默认评级循环：{_selected_rating_loop_text(item)}",
        *_format_jcl_record_detail_lines(item),
        f"可用评级JCL：{item.get('jcl_count', 0)} 个",
        "评级循环选择：装备评级 <服务器> <角色> <心法> 评级列表",
    ]
    if item.get("warning"):
        lines.append(f"提示：{item['warning']}")
    return "\n".join(lines)


async def _fetch_equipment_rating_loop_entries(
    event: GroupMessageEvent,
    instance: UniversalCalculator | JX3BOXCalculator,
) -> list[dict[str, Any]] | str:
    use_custom_loops = Preference(event.user_id, "", "").setting("计算器来源") == "自定义"
    return await _calculator_loop_entries(
        instance,
        event.user_id,
        use_custom_loops,
        public_error="该心法当前没有可用公共 JCL，默认装备评级仍可使用评级专用 JCL。",
    )


def _format_equipment_rating_loop_list(loops: list[dict[str, Any]]) -> str:
    return format_calculator_loop_selection(loops, "请选择装备评级循环，选择后会开始计算（列表与计算器循环列表一致）：")


def _equipment_rating_loop_payload(loop_entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": str(loop_entry.get("display_name") or ""),
        "weapon": str(loop_entry.get("weapon") or ""),
        "haste": str(loop_entry.get("haste") or ""),
        "loop": str(loop_entry.get("loop") or ""),
        "user_id": int(loop_entry.get("user_id") or 0),
    }


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


def _rating_group_qrcode() -> str:
    path = Path(build_path(ASSETS, ["image", "jx3", "equipment_rating", "group_qrcode.png"]))
    return path.as_uri() if path.exists() else ""


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


def _jx3_icon(icon_id: Any) -> str:
    icon_id_int = int(_to_float(icon_id))
    if icon_id_int <= 0:
        icon_id_int = 1434
    return f"https://icon.jx3box.com/icon/{icon_id_int}.png"


def _item_icon_by_name(name: str) -> str:
    if not name:
        return ""
    try:
        for item in TabCache.Item:
            if len(item) >= 5 and item[4] == name:
                return _jx3_icon(item[1])
    except Exception:
        return ""
    return ""


def _skill_icon_by_name(name: str) -> str:
    if not name:
        return ""
    try:
        for skill in TabCache.skill:
            if len(skill) >= 12 and skill[11] == name:
                return _jx3_icon(skill[2])
    except Exception:
        return ""
    return ""


def _formation_alias(name: str, item: dict[str, Any] | None = None) -> str:
    item = item if isinstance(item, dict) else {}
    alias = item.get("alias") or item.get("nickname") or ADAPTIVE_FORMATION_ALIASES.get(name, "")
    return str(alias).strip()


def _formation_fallback_icon(name: str) -> str:
    icon_id = ADAPTIVE_FORMATION_FALLBACK_ICON_IDS.get(name)
    if not icon_id:
        return ""
    return _jx3_icon(icon_id)


def _adaptive_icon(item: dict[str, Any]) -> str:
    category = str(item.get("category") or "")
    name = str(item.get("name") or "")
    if category == "阵眼":
        return (
            _skill_icon_by_name(name)
            or _formation_fallback_icon(name)
            or _asset_uri("image", "jx3", "attributes", "unknown.png")
        )
    for code in item.get("codes") or []:
        icon_name = ADAPTIVE_ICON_ITEM_NAME_BY_CODE.get(str(code))
        icon = _item_icon_by_name(icon_name or "")
        if icon:
            return icon
    icon = _item_icon_by_name(name)
    if icon:
        return icon
    return _asset_uri("image", "jx3", "attributes", "unknown.png")


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


def _prepare_ring_combination_notes(raw_items: Any) -> dict[int, str]:
    combinations = [
        item
        for item in raw_items or []
        if isinstance(item, dict) and _to_float(item.get("diff_dps")) > 0
    ]
    if not combinations:
        return {}
    best_combo = max(combinations, key=lambda item: _to_float(item.get("diff_dps")))
    names = [
        str(item.get("name") or "").strip()
        for item in best_combo.get("items") or []
        if isinstance(item, dict) and str(item.get("name") or "").strip()
    ]
    if len(names) < 2:
        return {}
    text = f"戒指最优组合[{' + '.join(names)}]：{_format_signed(best_combo.get('diff_dps'))}"
    notes = {}
    for location in best_combo.get("locations") or []:
        try:
            location_code = int(location)
        except (TypeError, ValueError):
            continue
        if location_code in {6, 7}:
            notes[location_code] = text
    return notes


def _prepare_slots(
    slots: list[dict[str, Any]],
    ring_combination_notes: dict[int, str] | None = None,
) -> list[dict[str, Any]]:
    prepared = []
    ring_combination_notes = ring_combination_notes or {}
    order = {location: index for index, location in enumerate(SLOT_DISPLAY_ORDER)}
    for slot in sorted(slots, key=lambda item: order.get(int(item.get("location_code", 99)), 99)):
        location_code = int(slot.get("location_code", 99))
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
            "ring_combination_note": ring_combination_notes.get(location_code, ""),
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
    is_therapy_rating = summary.get("metric") == "therapy_ruin_capacity" or attributes.get("kungfu_type") == "Therapy"
    role_info = [
        {"label": "门派", "value": kungfu.school or "-"},
        {"label": "心法", "value": kungfu.name or "-"},
        {"label": "主属性", "value": main_attr_label},
        {"label": "目标", "value": "10秒承压窗口" if is_therapy_rating else "134级木桩"},
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
    if is_therapy_rating:
        basic_attrs = [
            {"label": "装分", "value": _format_number(summary.get("current_score"))},
            {"label": "基础治疗", "value": _format_number(attributes.get("BaseTherapy"))},
            {"label": "最终治疗", "value": _format_number(attributes.get("FinalTherapy"))},
            {"label": main_attr_label, "value": _format_number(attributes.get("MainAttrValue"))},
        ]
        detail_attrs = [
            {"label": "会心", "value": _format_percent(_to_float(attributes.get("Critical")) * 100)},
            {"label": "会效", "value": _format_percent(_to_float(attributes.get("CriticalDamage")) * 100)},
            {"label": "加速", "value": _format_haste(attributes.get("Haste"))},
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
        label = str(item.get("name") or "").strip() or get_attr_name(attribute_key) or str(item.get("key") or "").strip()
        if label == "会心效果":
            label = "会效"
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


def _prepare_adaptive_haste(raw: Any) -> dict[str, str] | None:
    if not isinstance(raw, dict):
        return None
    required = int(_to_float(raw.get("required")))
    actual = int(_to_float(raw.get("actual")))
    if required <= 0:
        return None
    satisfied = bool(raw.get("satisfied"))
    delta = actual - required
    if satisfied:
        status_text = "已满足"
        detail_parts = [
            f"当前 {_format_number(actual)}（{_haste_level(actual)}段）",
            f"目标 {_format_number(required)}（{_haste_level(required)}段）",
        ]
        if delta > 0:
            detail_parts.append(f"溢出 {_format_number(delta)}")
        return {
            "state": "ok",
            "status": status_text,
            "detail": " · ".join(detail_parts),
        }
    return {
        "state": "missing",
        "status": "未满足",
        "detail": " · ".join(
            [
                f"当前 {_format_number(actual)}（{_haste_level(actual)}段）",
                f"目标 {_format_number(required)}（{_haste_level(required)}段）",
                f"还差 {_format_number(abs(delta))}",
            ]
        ),
    }


def _prepare_adaptive_formation(item: Any, rank: int | None = None) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None
    category = str(item.get("category") or "阵眼").strip()
    name = str(item.get("name") or "").strip()
    if category != "阵眼" or not name:
        return None
    note_parts = []
    alias = _formation_alias(name, item)
    if alias:
        note_parts.append(alias)
    side_effect = str(item.get("side_effect") or "").strip()
    if side_effect:
        note_parts.append(side_effect)
    return {
        "category": category,
        "name": name,
        "icon": _adaptive_icon({**item, "category": category}),
        "note": " · ".join(note_parts),
        "label": f"第{rank}名" if rank else "推荐阵法",
        "rank_icon": _grade_icon(ADAPTIVE_FORMATION_RANK_GRADES.get(rank, "")) if rank else "",
        "rank": rank,
        "delta_text": _format_signed_percent(item.get("delta_percent")),
        "is_adaptive": item.get("source") == "adaptive",
    }


def _prepare_adaptive_consumables(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    status = str(raw.get("status") or "")
    if status != "ok":
        message = str(raw.get("message") or "自适应小药计算失败，已跳过展示。")
        return {
            "status": "failed",
            "message": message,
            "entries": [],
        }
    group_index = {
        category: index
        for index, (_, _, categories) in enumerate(ADAPTIVE_DISPLAY_GROUPS)
        for category in categories
    }
    grouped_items = [
        {
            "key": key,
            "category": label,
            "entries": [],
        }
        for key, label, _ in ADAPTIVE_DISPLAY_GROUPS
    ]
    formation = None
    formation_entries = []
    flat_items = []
    for item in raw.get("items") or []:
        if not isinstance(item, dict):
            continue
        category = str(item.get("category") or "").strip()
        name = str(item.get("name") or "").strip()
        if not category or not name:
            continue
        note_parts = []
        side_effect = str(item.get("side_effect") or "").strip()
        if side_effect:
            note_parts.append(side_effect)
        prepared_item = {
            "category": category,
            "name": name,
            "icon": _adaptive_icon(item),
            "note": " · ".join(note_parts),
            "is_adaptive": item.get("source") == "adaptive",
        }
        if category == "阵眼":
            formation = _prepare_adaptive_formation(item, 1) or prepared_item
            flat_items.insert(0, formation)
            continue
        index = group_index.get(category)
        if index is None:
            continue
        grouped_items[index]["entries"].append(prepared_item)
        flat_items.append(prepared_item)
    for index, item in enumerate(raw.get("formation_top") or [], start=1):
        prepared_formation = _prepare_adaptive_formation(item, index)
        if prepared_formation:
            formation_entries.append(prepared_formation)
    if not formation_entries and formation:
        formation_entries = [formation]
    if formation_entries:
        formation = formation_entries[0]
    groups = [group for group in grouped_items if group["entries"]]
    if not formation and not groups:
        return None
    baseline = _as_dict(raw.get("baseline"))
    summary_parts = []
    if baseline.get("formation_delta_percent") is not None:
        summary_parts.append(f"阵眼 {_format_signed_percent(baseline.get('formation_delta_percent'))}")
    return {
        "status": "ok",
        "title": str(raw.get("name") or "当前装备自适应小药"),
        "subtitle": str(raw.get("subtitle") or "基于当前配装与目标加速档自动推荐"),
        "summary": " / ".join(summary_parts),
        "metric_name": str(raw.get("metric_name") or "最终DPS"),
        "metric_unit": str(raw.get("metric_unit") or "DPS"),
        "dps_text": _format_compact_number(raw.get("dps")),
        "raw_dps_text": _format_compact_number(raw.get("raw_dps")),
        "delta_text": _format_signed(raw.get("delta")),
        "delta_percent_text": _format_signed_percent(raw.get("delta_percent")),
        "full_income_codes": [str(code) for code in raw.get("full_income_codes") or [] if str(code)],
        "haste": _prepare_adaptive_haste(raw.get("haste")),
        "formation": formation,
        "formations": formation_entries,
        "groups": groups,
        "entries": flat_items,
    }


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


def _tank_vitality_conversion_item(
    attributes: dict[str, Any],
    *,
    title: str,
    formula_label: str,
) -> dict[str, str] | None:
    base_vitality = int(_to_float(attributes.get("BaseVitality")))
    if base_vitality <= 0:
        return None
    stacks = min(base_vitality // TANK_VITALITY_CONVERSION_STEP, TANK_VITALITY_CONVERSION_MAX_STACKS)
    effective_vitality = stacks * TANK_VITALITY_CONVERSION_STEP
    next_delta = (
        0
        if stacks >= TANK_VITALITY_CONVERSION_MAX_STACKS or base_vitality == effective_vitality
        else (stacks + 1) * TANK_VITALITY_CONVERSION_STEP - base_vitality
    )
    return {
        "title": title,
        "formula_label": formula_label,
        "stacks": str(stacks),
        "vitality": _format_number(base_vitality),
        "effective_vitality": _format_number(effective_vitality),
        "next_delta": _format_number(next_delta),
        "step": _format_number(TANK_VITALITY_CONVERSION_STEP),
        "max_stacks": str(TANK_VITALITY_CONVERSION_MAX_STACKS),
    }


def _prepare_tank_vitality_conversion(summary: dict[str, Any], kungfu: Kungfu) -> dict[str, Any] | None:
    if kungfu.abbr != "T":
        return None
    unbuffed_item = _tank_vitality_conversion_item(
        summary.get("unbuffed_attributes") or {},
        title="裸小药",
        formula_label="裸小药基础体质",
    )
    full_item = _tank_vitality_conversion_item(
        summary.get("attributes") or {},
        title="满小药",
        formula_label="满小药基础体质",
    )
    item = unbuffed_item or full_item
    if item is None:
        return None
    if unbuffed_item is not None and full_item is not None:
        item["full_stacks"] = f"{full_item['stacks']}层"
    return item


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
    timeline_data: dict[str, Any] | None = None,
    rank_data: dict[str, Any] | None = None,
):
    meta = data["meta"]
    summary = data["summary"]
    kungfu = Kungfu.with_internel_id(meta["kungfu_id"])
    theme_color = kungfu.color if kungfu.name else "#4f6f87"
    is_therapy_rating = summary.get("metric") == "therapy_ruin_capacity"
    trial_land = (
        _prepare_trial_land(data.get("trial_land"))
        if kungfu.abbr == "D" and not is_therapy_rating
        else None
    )
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
    slots = _prepare_slots(
        data["slots"],
        _prepare_ring_combination_notes(data.get("combination_recommendations")),
    )
    chips = [
        meta.get("loop_name", "评级专用循环"),
        f"{meta.get('jcl', {}).get('weapon', '')}{meta.get('jcl', {}).get('haste', '')}",
        meta.get("income_name", "默认增益"),
        f"{summary.get('metric_name') or '承压能力'} {_format_number(summary.get('current_dps'))}" if is_therapy_rating else "",
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
            "title": (
                f"{kungfu.name}承压报告"
                if is_therapy_rating and kungfu.name
                else (f"{kungfu.name}体检报告" if kungfu.name else "体检报告")
            ),
        },
        role_info=role_info,
        basic_attrs=basic_attrs,
        detail_attrs=detail_attrs,
        attribute_incomes=_prepare_attribute_incomes(summary),
        adaptive_consumables=_prepare_adaptive_consumables(data.get("adaptive_consumables")),
        trial_land=trial_land,
        equipment_rating_rank=rank_data,
        rating_timeline=_prepare_rating_timeline(timeline_data),
        equipment_rating_qrcode=_rating_group_qrcode(),
        tank_vitality_conversion=_prepare_tank_vitality_conversion(summary, kungfu),
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
    *,
    refresh_tuilan: bool = True,
):
    player_data = await _try_resolve_equipment_rating_player(server, role_id, refresh_tuilan=refresh_tuilan)
    if player_data is None:
        await matcher.finish(PROMPT.PlayerNotExist)
    return player_data


async def _try_resolve_equipment_rating_player(
    server: str,
    role_id: str,
    *,
    refresh_tuilan: bool = True,
):
    try:
        if role_id.isdigit():
            player_data = await search_player(role_name=role_id, role_id=role_id, server_name=server, local_lookup=True)
            if player_data.roleId == "":
                player_data = await get_uid_data(role_id=role_id, server=server, msg=False)
        else:
            player_data = await search_player(role_name=role_id, server_name=server)
        if player_data.roleId == "":
            return None
        if refresh_tuilan:
            await JX3PlayerAttribute.from_tuilan(player_data.roleId, player_data.serverName, player_data.globalRoleId)
        return player_data
    except Exception:
        return None


def _auto_select_rating_pve_tag(kungfu_id: int) -> str | None:
    if kungfu_id in SPECIAL_PVE_KUNGFU_TAGS:
        return SPECIAL_PVE_KUNGFU_TAGS[kungfu_id]
    abbr = Kungfu.with_internel_id(kungfu_id).abbr
    if abbr == "T":
        return "TPVE"
    if abbr == "N":
        return "HPSPVE"
    if abbr == "D":
        return "DPSPVE"
    return None


async def _rating_pve_kungfu_options(global_role_id: int) -> list[dict[str, Any]]:
    all_equips = await JX3PlayerAttribute.from_database(global_role_id, "", True)
    if not all_equips:
        return []

    latest_by_kungfu: dict[int, JX3PlayerAttribute] = {}
    for equip in all_equips:
        kungfu_id = int(equip.kungfu_id)
        if equip.tag != "PVE":
            continue
        tag = _auto_select_rating_pve_tag(kungfu_id)
        if tag is None:
            continue
        current = latest_by_kungfu.get(kungfu_id)
        if current is None or equip.timestamp > current.timestamp:
            latest_by_kungfu[kungfu_id] = equip

    options: list[dict[str, Any]] = []
    for kungfu_id, equip in sorted(latest_by_kungfu.items(), key=lambda item: item[1].timestamp, reverse=True):
        kungfu = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True)
        tag = _auto_select_rating_pve_tag(kungfu_id)
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


async def _default_rating_pve_kungfu_id(global_role_id: int) -> int | None:
    equip = await JX3PlayerAttribute.from_database(global_role_id, "DPSPVE", False)
    if equip is None:
        return None
    return int(equip.kungfu_id)


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


async def _build_equipment_rating_payload_by_pzid(
    matcher: Matcher,
    pzid: int,
) -> tuple[dict[str, Any], str, str, None]:
    instance = await JX3BOXCalculator.with_pzid(pzid)
    if isinstance(instance, str):
        await matcher.finish(instance)
    payload = {
        "kungfu_id": int(instance.kungfu_id),
        "jcl_data": normalize_calculator_jcl_data(instance.jcl_data),
        "role": {
            "name": f"魔盒配装 {pzid}",
            "server": "JX3BOX",
            "global_role_id": 0,
        },
        "candidate_level": {
            "min": 32500,
            "max": 43000,
        },
    }
    return payload, f"魔盒配装 {pzid}", "JX3BOX", None


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
    rating_equip: JX3PlayerAttribute | None,
    role_id: str = "",
    global_role_id: int = 0,
):
    rating_payload = {**payload, "include_trial_land": True}
    data = await _request_equipment_rating_data(rating_payload)
    if isinstance(data, str):
        await matcher.finish(data)
    if global_role_id <= 0 and rating_equip is not None:
        global_role_id = int(rating_equip.global_role_id)
    rank_data = None
    if rating_equip is not None:
        try:
            rank_data = record_equipment_rating_rank(data, role_name, server_name, role_id, global_role_id)
        except Exception as exc:
            logger.warning(f"装备评级排名记录失败：{exc}")
    timeline_data = await _request_equipment_rating_timeline(data, payload)
    await finish_equipment_rating_response(
        matcher,
        await render_equipment_rating_image(data, role_name, server_name, rating_equip, timeline_data, rank_data)
    )


async def _resolve_bare_equipment_rating_kungfu_id(
    matcher: Matcher,
    state: T_State,
    global_role_id: int,
    server: str,
    role_arg: str,
    use_public_loop_list: bool,
) -> int | None:
    options = await _rating_pve_kungfu_options(global_role_id)
    if len(options) == 1:
        return int(options[0]["kungfu_id"])
    if len(options) > 1:
        state["equipment_rating_kungfu_options"] = options
        state["equipment_rating_server"] = server
        state["equipment_rating_role_arg"] = role_arg
        state["equipment_rating_use_public_loop_list"] = use_public_loop_list
        await matcher.send(_format_special_pve_kungfu_selection(options))
        return None

    kungfu_id = await _default_rating_pve_kungfu_id(global_role_id)
    if kungfu_id is None:
        await matcher.finish("未指定心法，且未找到该玩家可用于自动选择的 PVE 心法装备，请使用：装备评级 <服务器> <角色名> <心法>")
    return kungfu_id


async def _handle_equipment_rating_pzid(
    event: GroupMessageEvent,
    matcher: Matcher,
    state: T_State,
    pzid: int,
    use_public_loop_list: bool,
):
    payload, role_name, server_name, rating_equip = await _build_equipment_rating_payload_by_pzid(matcher, pzid)
    kungfu_id = int(payload["kungfu_id"])
    if use_public_loop_list:
        loop_instance = JX3BOXCalculator(kungfu_id=kungfu_id)
        loops = await _fetch_equipment_rating_loop_entries(event, loop_instance)
        if isinstance(loops, str):
            await matcher.finish(loops)
        state["equipment_rating_pzid"] = pzid
        state["equipment_rating_kungfu_id"] = kungfu_id
        state["equipment_rating_loops"] = loops
        await matcher.send(_format_equipment_rating_loop_list(loops))
        return

    await _send_equipment_rating_started(matcher)
    await _finish_equipment_rating_calculation(
        matcher,
        payload,
        role_name,
        server_name,
        rating_equip,
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
    if len(arg) not in [1, 2, 3, 4]:
        await matcher.finish(PROMPT.ArgumentCountInvalid + "\n" + EQUIPMENT_RATING_USAGE)
    use_public_loop_list = False
    if arg[-1] in RATING_LOOP_LIST_KEYWORDS:
        use_public_loop_list = True
        arg = arg[:-1]
    if len(arg) not in [1, 2, 3]:
        await matcher.finish("评级列表参数仅支持放在命令末尾，用于选择评级循环。\n" + EQUIPMENT_RATING_USAGE)

    if len(arg) == 1:
        if not arg[0].isdigit():
            await matcher.finish(PROMPT.ArgumentCountInvalid + "\n" + EQUIPMENT_RATING_USAGE)
        await _handle_equipment_rating_pzid(event, matcher, state, int(arg[0]), use_public_loop_list)
        return

    server = Server(arg[0], event.group_id).server
    if server is None:
        await matcher.finish(PROMPT.ServerNotExist)

    resolved_player_data = None
    if len(arg) == 2 and arg[1].isdigit():
        resolved_player_data = await _try_resolve_equipment_rating_player(server, arg[1])
        if resolved_player_data is None:
            await _handle_equipment_rating_pzid(event, matcher, state, int(arg[1]), use_public_loop_list)
            return

    if len(arg) == 2:
        player_data = resolved_player_data or await _resolve_equipment_rating_player(matcher, server, arg[1])
        kungfu_id = await _resolve_bare_equipment_rating_kungfu_id(
            matcher,
            state,
            int(player_data.globalRoleId),
            server,
            arg[1],
            use_public_loop_list,
        )
        if kungfu_id is None:
            return
    else:
        kungfu_id = Kungfu(arg[2]).id
        if kungfu_id is None:
            await matcher.finish(PROMPT.KungfuNotExist)

    if use_public_loop_list:
        loop_instance = UniversalCalculator(kungfu_id=kungfu_id)
        loops = await _fetch_equipment_rating_loop_entries(event, loop_instance)
        if isinstance(loops, str):
            await matcher.finish(loops)
        state["equipment_rating_server"] = server
        state["equipment_rating_role_arg"] = arg[1]
        state["equipment_rating_kungfu_id"] = kungfu_id
        state["equipment_rating_loops"] = loops
        await matcher.send(_format_equipment_rating_loop_list(loops))
        return

    await _send_equipment_rating_started(matcher)
    payload, player_data, rating_equip = await _build_equipment_rating_payload_by_kungfu(matcher, server, arg[1], kungfu_id)
    await _finish_equipment_rating_calculation(
        matcher,
        payload,
        player_data.roleName,
        player_data.serverName,
        rating_equip,
        player_data.roleId,
        int(player_data.globalRoleId),
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
            loop_instance = UniversalCalculator(kungfu_id=kungfu_id)
            loops = await _fetch_equipment_rating_loop_entries(event, loop_instance)
            if isinstance(loops, str):
                await matcher.finish(loops)
            state["equipment_rating_kungfu_id"] = kungfu_id
            state["equipment_rating_loops"] = loops
            await matcher.send(_format_equipment_rating_loop_list(loops))
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
            player_data.roleId,
            int(player_data.globalRoleId),
        )

    loops = state.get("equipment_rating_loops")
    pzid = state.get("equipment_rating_pzid")
    if isinstance(loops, list) and isinstance(pzid, int):
        index = int(num)
        if index < 1 or index > len(loops):
            await matcher.finish("超出可选范围，请重新发起命令！")
        await _send_equipment_rating_started(matcher)
        payload, role_name, server_name, rating_equip = await _build_equipment_rating_payload_by_pzid(matcher, pzid)
        payload = {**payload, "jcl_loop": _equipment_rating_loop_payload(loops[index - 1])}
        await _finish_equipment_rating_calculation(
            matcher,
            payload,
            role_name,
            server_name,
            rating_equip,
        )
        return

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
    payload = {**payload, "jcl_loop": _equipment_rating_loop_payload(loops[index - 1])}
    await _finish_equipment_rating_calculation(
        matcher,
        payload,
        player_data.roleName,
        player_data.serverName,
        rating_equip,
        player_data.roleId,
        int(player_data.globalRoleId),
    )
