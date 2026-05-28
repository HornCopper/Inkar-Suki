from functools import lru_cache
from pathlib import Path
import html as H
import json
import re

from jinja2 import Template
from nonebot.adapters.onebot.v11 import Message, MessageSegment as ms

from src.config import Config
from src.const.path import ASSETS, build_path
from src.templates import HTMLSourceCode
from src.utils.analyze import check_number
from src.utils.generate import generate
from src.utils.network import Request, cache_image

from ._template import table_head_skill, template_body_skill


NOUN_PATH = build_path(ASSETS, ["source", "jx3", "tabs", "Skill_Nouns.txt"])
NOUN_PATTERN = re.compile(r"<NounID\s+(\d+)>")


@lru_cache(maxsize=1)
def _load_skill_nouns() -> dict[str, tuple[str, str]]:
    with open(NOUN_PATH, encoding="gbk") as noun_file:
        rows = [line.rstrip("\n").split("\t") for line in noun_file]
    result = {}
    for row in rows[1:]:
        if len(row) >= 3:
            result[row[0]] = (row[1], row[2])
    return result


def _decode_desc(desc: str) -> str:
    try:
        return json.loads(f'"{desc}"').replace("。<", "。\n<").replace("><", ">\n<")
    except json.JSONDecodeError:
        desc = desc.replace('"', '\\"')
        return json.loads(f'"{desc}"').replace("。<", "。\n<").replace("><", ">\n<")


def _expand_noun_tags(desc: str, *, append_details: bool = True, _seen: set[str] | None = None) -> str:
    nouns = _load_skill_nouns()
    seen = set() if _seen is None else _seen
    used_ids: list[str] = []

    def replace(match: re.Match[str]) -> str:
        noun_id = match.group(1)
        noun = nouns.get(noun_id)
        if noun is None:
            return match.group(0)
        if noun_id not in used_ids:
            used_ids.append(noun_id)
        return f"[{noun[0]}]"

    expanded = NOUN_PATTERN.sub(replace, desc)
    if not append_details:
        return expanded

    details = []
    for noun_id in used_ids:
        if noun_id in seen:
            continue
        noun_name, noun_desc = nouns[noun_id]
        seen.add(noun_id)
        detail_desc = _expand_noun_tags(_decode_desc(noun_desc), append_details=True, _seen=seen)
        details.append(f"[{noun_name}]：{detail_desc}")
    if details:
        expanded += "\n" + "\n".join(details)
    return expanded


def _format_skill_desc(desc: str) -> str:
    return _expand_noun_tags(_decode_desc(desc))


async def get_skill(skill_keyword: str = "") -> str | Message | ms:
    if "_" in skill_keyword:
        if not re.match(r"^\d+_\d+$", skill_keyword):
            return "请检查技能ID和技能等级的格式，仅接受 技能ID_技能等级 格式，或请使用技能名查询。"
        skill_id, skill_level = skill_keyword.split("_")
        params = {
            "skill_id": int(skill_id),
            "skill_level": int(skill_level)
        }
    elif check_number(skill_keyword):
        params = {
            "skill_id": int(skill_keyword)
        }
    else:
        params = {
            "skill_name": skill_keyword
        }
    data = (await Request(f"{Config.jx3.api.calculator_url}/skill", params=params).get()).json()
    if data["code"] != 200:
        return "未找到相关技能，请检查后重试！"
    if len(data["data"]) == 1:
        skill = data["data"][0]
        image = await cache_image("https://icon.jx3box.com/icon/" + skill["IconID"] + ".png")
        remark = skill["Remark"]
        desc = _format_skill_desc(skill["Desc"])
        name = skill["Name"]
        return ms.image(
            Request(Path(image).as_uri()).local_content
        ) + f"技能名：{name}\n备注：{remark}\n{desc}"

    skills = data["data"]
    if len(skills) > 30:
        skills = skills[:30]
    tables = []
    for skill in skills:
        desc = _format_skill_desc(skill["Desc"])
        tables.append(
            Template(template_body_skill).render(
                icon=Path(await cache_image("https://icon.jx3box.com/icon/" + skill["IconID"] + ".png")).as_uri(),
                skill_id=skill["SkillID"] + "_" + skill["Level"],
                name=skill["Name"],
                remark=skill["Remark"],
                desc=H.escape(desc).replace("\n", "<br>")
            )
        )
    html = str(
        HTMLSourceCode(
            application_name="技能表",
            table_head=table_head_skill,
            table_body="\n".join(tables)
        )
    )
    image = await generate(html, ".container", True, segment=True)
    return image


async def get_buff(buff_keyword: str = "") -> str | Message | ms:
    if "_" in buff_keyword:
        if not re.match(r"^\d+_\d+$", buff_keyword):
            return "请检查气劲ID和气劲等级的格式，仅接受 气劲ID_气劲等级 格式，或请使用气劲名查询。"
        buff_id, buff_level = buff_keyword.split("_")
        params = {
            "buff_id": int(buff_id),
            "buff_level": int(buff_level)
        }
    elif check_number(buff_keyword):
        params = {
            "buff_id": int(buff_keyword)
        }
    else:
        params = {
            "buff_name": buff_keyword
        }
    data = (await Request(f"{Config.jx3.api.calculator_url}/buff", params=params).get()).json()
    if data["code"] != 200:
        return "未找到相关气劲，请检查后重试！"
    if len(data["data"]) == 1:
        buff = data["data"][0]
        image = await cache_image("https://icon.jx3box.com/icon/" + buff["IconID"] + ".png")
        remark = buff["Remark"]
        desc = _decode_desc(buff["Desc"])
        name = buff["Name"]
        return ms.image(
            Request(Path(image).as_uri()).local_content
        ) + f"气劲名：{name}\n备注：{remark}\n{desc}"

    buffs = data["data"]
    if len(buffs) > 30:
        buffs = buffs[:30]
    tables = []
    for buff in buffs:
        desc = _decode_desc(buff["Desc"])
        tables.append(
            Template(template_body_skill).render(
                icon=Path(await cache_image("https://icon.jx3box.com/icon/" + buff["IconID"] + ".png")).as_uri(),
                skill_id=buff["BuffID"] + "_" + buff["Level"],
                name=buff["Name"],
                remark=buff["Remark"],
                desc=H.escape(desc).replace("\n", "<br>")
            )
        )
    html = str(
        HTMLSourceCode(
            application_name="气劲表",
            table_head=table_head_skill,
            table_body="\n".join(tables)
        )
    )
    image = await generate(html, ".container", True, segment=True)
    return image
