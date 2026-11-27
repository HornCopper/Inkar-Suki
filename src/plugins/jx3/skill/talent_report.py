"""奇穴报告的分重展示、共用候选池合并和描述标注。"""

from pathlib import Path
import re
from typing import TYPE_CHECKING

from jinja2 import Environment
from markupsafe import Markup, escape

from src.const.jx3.kungfu import Kungfu
from src.const.path import ASSETS, TEMPLATES

if TYPE_CHECKING:
    from .talent import QixueInfo


_DESCRIPTION_MARKER = re.compile(r"(?P<requirement>【需求核心奇穴\s+[^】\r\n]+】)|\[[^\]\r\n]+\]")


def _format_description(description: str) -> Markup:
    # 先转义原文，再仅给名词和前置要求添加受控的样式标记。
    def annotate(match: re.Match[str]) -> str:
        css_class = "talent-requirement" if match["requirement"] else "noun-reference"
        return f'<span class="{css_class}">{match[0]}</span>'

    return Markup(_DESCRIPTION_MARKER.sub(annotate, str(escape(description))))


def _tier_label(tiers: list[int]) -> str:
    if len(tiers) == 1:
        return f"第{tiers[0]}重"
    if tiers == list(range(tiers[0], tiers[-1] + 1)):
        return f"第{tiers[0]}—{tiers[-1]}重"
    return "第" + "、".join(map(str, tiers)) + "重"


def build_talent_report(talents: list["QixueInfo"]) -> dict:
    tiers: dict[tuple[str, int], list[QixueInfo]] = {}
    for talent in talents:
        tiers.setdefault((getattr(talent, "kungfu", ""), talent.location[0]), []).append(talent)
    sections = []
    pools = {}
    for (kungfu, tier), options in sorted(tiers.items()):
        options = sorted(options, key = lambda option: option.location[1])
        signature = (kungfu, tuple((option.location[1], option.name, option.icon, option.desc) for option in options))
        if signature in pools:
            pools[signature]["tiers"].append(tier)
            continue
        entries = []
        for option in options:
            entries.append({"position": option.location[1], "name": option.name, "icon": option.icon,
                            "description": option.desc})
        section = {"kungfu": kungfu, "tiers": [tier], "entries": entries}
        pools[signature] = section
        sections.append(section)
    for section in sections:
        section["label"] = _tier_label(section["tiers"])
    return {"sections": sections, "tier_count": len(tiers),
            "kungfu_count": len({kungfu for kungfu, _ in tiers}),
            "entry_count": sum(len(section["entries"]) for section in sections)}


def render_talent_report(talents: list["QixueInfo"], kungfu: str, season: str = "", keyword: str = "") -> str:
    report = build_talent_report(talents)
    if not kungfu:
        for section in report["sections"]:
            section_kungfu = Kungfu(section["kungfu"])
            section["kungfu_icon"] = Path(section_kungfu.icon).as_uri()
            section["kungfu_color"] = section_kungfu.color
    source = Path(TEMPLATES, "jx3", "talents.html").read_text(encoding = "utf-8")
    environment = Environment(autoescape = True)
    environment.filters["format_description"] = _format_description
    return environment.from_string(source).render(
        report = report, kungfu = kungfu or "所有心法", show_kungfu = not kungfu,
        season = season or "最新", keyword = keyword,
        font = Path(ASSETS, "font", "PingFangSC-Medium.otf").as_uri(),
    )
