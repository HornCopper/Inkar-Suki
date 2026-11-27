from pathlib import Path
import html as H
import json
import re

from jinja2 import Template
from nonebot.adapters.onebot.v11 import Message, MessageSegment as ms

from src.config import Config
from src.templates import HTMLSourceCode
from src.utils.analyze import check_number
from src.utils.generate import generate
from src.utils.jx3_icons import icon_url
from src.utils.jx3_skill_desc import format_skill_description, load_skill_icons
from src.utils.network import Request, cache_image

from ._template import skill_table_css, table_head_skill, template_body_skill

def _decode_desc(desc: str) -> str:
    try:
        return json.loads(f'"{desc}"').replace("。<", "。\n<").replace("><", ">\n<")
    except json.JSONDecodeError:
        desc = desc.replace("\"", "\\\"")
        return json.loads(f'"{desc}"').replace("。<", "。\n<").replace("><", ">\n<")

def _format_skill_desc(desc: str, *, talent_references: list[tuple[int, int, str]] | None = None) -> str:
    return format_skill_description(desc, talent_references = talent_references).replace("。<", "。\n<").replace("><", ">\n<")

def _format_skill_desc_html(desc: str, talent_references: list[tuple[int, int, str]] | None = None) -> str:
    def format_text(text: str) -> str:
        return re.sub(r"\[[^\]\r\n]+\]", lambda match: f'<span class="noun-reference">{match[0]}</span>', H.escape(text))

    lines = []
    is_talent = False
    icons = load_skill_icons() if talent_references else {}
    talent_icons = {}
    for skill_id, level, name in talent_references or []:
        icon = icons.get((skill_id, level)) or icons.get((skill_id, 0)) or icons.get((skill_id, 1))
        talent_icons.setdefault(name, []).append(icon)
    for line in desc.split("\n"):
        escaped = format_text(line)
        if line.startswith("【奇穴 "):
            is_talent = True
            match = re.match(r"^【奇穴 ([^】]+)】", line)
            if match:
                escaped = f'{format_text(match[1])}：{format_text(line[match.end():])}'
                if talent_icons.get(match[1]):
                    icon = talent_icons[match[1]].pop(0)
                    if icon:
                        source = H.escape(icon_url(icon), quote = True)
                        escaped = f'<img class="skill-talent-icon" src="{source}" alt=""> {escaped}'
        elif re.match(r"^\[[^\]\r\n]+\]：", line):
            is_talent = False
        lines.append(f'<span class="skill-talent-effect">{escaped}</span>' if is_talent else escaped)
    return "<br>".join(lines)

async def get_skill(skill_keyword: str = "") -> str | Message | ms:
    if "_" in skill_keyword:
        if not re.match(r"^\d+_\d+$", skill_keyword):
            return "请检查技能ID和技能等级的格式，仅接受 技能ID_技能等级 格式，或请使用技能名查询。"
        skill_id, skill_level = skill_keyword.split("_")
        params = {
            "skill_id": int(skill_id),
            "skill_level": int(skill_level),
        }
    elif check_number(skill_keyword):
        params = {
            "skill_id": int(skill_keyword),
        }
    else:
        params = {
            "skill_name": skill_keyword,
        }
    data = (await Request(f"{Config.jx3.api.calculator_url}/skill", params = params).get()).json()
    if data["code"] != 200:
        return "未找到相关技能，请检查后重试！"
    if len(data["data"]) == 1:
        skill = data["data"][0]
        image = await cache_image("https://icon.jx3box.com/icon/" + skill["IconID"] + ".png")
        remark = skill["Remark"]
        desc = _format_skill_desc(skill.get("DisplayDesc") or skill["Desc"])
        name = skill["Name"]
        return ms.image(
            Request(Path(image).as_uri()).local_content,
        ) + f"技能名：{name}\n备注：{remark}\n{desc}"

    skills = data["data"]
    if len(skills) > 30:
        skills = skills[:30]
    tables = []
    for skill in skills:
        talent_references = []
        desc = _format_skill_desc(skill.get("DisplayDesc") or skill["Desc"], talent_references = talent_references)
        tables.append(
            Template(template_body_skill).render(
                icon = Path(await cache_image("https://icon.jx3box.com/icon/" + skill["IconID"] + ".png")).as_uri(),
                skill_id = skill["SkillID"] + "_" + skill["Level"],
                name = skill["Name"],
                remark = skill["Remark"],
                desc = _format_skill_desc_html(desc, talent_references),
            ),
        )
    html = str(
        HTMLSourceCode(
            application_name = "技能表",
            additional_css = skill_table_css,
            table_head = table_head_skill,
            table_body = "\n".join(tables),
        ),
    )
    image = await generate(html, ".container", True, segment = True)
    return image

async def get_buff(buff_keyword: str = "") -> str | Message | ms:
    if "_" in buff_keyword:
        if not re.match(r"^\d+_\d+$", buff_keyword):
            return "请检查气劲ID和气劲等级的格式，仅接受 气劲ID_气劲等级 格式，或请使用气劲名查询。"
        buff_id, buff_level = buff_keyword.split("_")
        params = {
            "buff_id": int(buff_id),
            "buff_level": int(buff_level),
        }
    elif check_number(buff_keyword):
        params = {
            "buff_id": int(buff_keyword),
        }
    else:
        params = {
            "buff_name": buff_keyword,
        }
    data = (await Request(f"{Config.jx3.api.calculator_url}/buff", params = params).get()).json()
    if data["code"] != 200:
        return "未找到相关气劲，请检查后重试！"
    if len(data["data"]) == 1:
        buff = data["data"][0]
        image = await cache_image("https://icon.jx3box.com/icon/" + buff["IconID"] + ".png")
        remark = buff["Remark"]
        desc = _decode_desc(buff["Desc"])
        name = buff["Name"]
        return ms.image(
            Request(Path(image).as_uri()).local_content,
        ) + f"气劲名：{name}\n备注：{remark}\n{desc}"

    buffs = data["data"]
    if len(buffs) > 30:
        buffs = buffs[:30]
    tables = []
    for buff in buffs:
        desc = _decode_desc(buff["Desc"])
        tables.append(
            Template(template_body_skill).render(
                icon = Path(await cache_image("https://icon.jx3box.com/icon/" + buff["IconID"] + ".png")).as_uri(),
                skill_id = buff["BuffID"] + "_" + buff["Level"],
                name = buff["Name"],
                remark = buff["Remark"],
                desc = H.escape(desc).replace("\n", "<br>"),
            ),
        )
    html = str(
        HTMLSourceCode(
            application_name = "气劲表",
            table_head = table_head_skill,
            table_body = "\n".join(tables),
        ),
    )
    image = await generate(html, ".container", True, segment = True)
    return image
