from pathlib import Path
from jinja2 import Template
from nonebot.adapters.onebot.v11 import Message, MessageSegment as ms

from src.config import Config
from src.const.jx3.kungfu import Kungfu
from src.const.jx3.school import School
from src.utils.network import Request, cache_image
from src.utils.analyze import check_number
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from ._template import template_body_skill, table_head_skill

import re
import json
import html as H

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
        desc = skill["Desc"]
        desc = json.loads(f'"{desc}"').replace("。<", "。\n<").replace("><", ">\n<")
        name = skill["Name"]
        return ms.image(
            Request(Path(image).as_uri()).local_content
        ) + f"技能名：{name}\n备注：{remark}\n{desc}"
    else:
        skills = data["data"]
        if len(skills) > 30:
            skills = skills[:30]
        tables = []
        for skill in skills:
            desc = skill["Desc"]
            tables.append(
                Template(template_body_skill).render(
                    icon = Path(await cache_image("https://icon.jx3box.com/icon/" + skill["IconID"] + ".png")).as_uri(),
                    skill_id = skill["SkillID"] + "_" + skill["Level"],
                    name = skill["Name"],
                    remark = skill["Remark"],
                    desc = H.escape(desc).replace("。&lt;", "。<br>&lt;").replace("&gt;&lt;", "&gt;<br>&lt;")
                )
            )
        html = str(
            HTMLSourceCode(
                application_name = "技能表",
                table_head = table_head_skill,
                table_body = "\n".join(tables)
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
        desc = buff["Desc"]
        desc = json.loads(f'"{desc}"').replace("。<", "。\n<").replace("><", ">\n<")
        name = buff["Name"]
        return ms.image(
            Request(Path(image).as_uri()).local_content
        ) + f"气劲名：{name}\n备注：{remark}\n{desc}"
    else:
        buffs = data["data"]
        if len(buffs) > 30:
            buffs = buffs[:30]
        tables = []
        for buff in buffs:
            desc = buff["Desc"]
            tables.append(
                Template(template_body_skill).render(
                    icon = Path(await cache_image("https://icon.jx3box.com/icon/" + buff["IconID"] + ".png")).as_uri(),
                    buff_id = buff["buffID"] + "_" + buff["Level"],
                    name = buff["Name"],
                    remark = buff["Remark"],
                    desc = H.escape(desc).replace("。&lt;", "。<br>&lt;").replace("&gt;&lt;", "&gt;<br>&lt;")
                )
            )
        html = str(
            HTMLSourceCode(
                application_name = "气劲表",
                table_head = table_head_skill,
                table_body = "\n".join(tables)
            )
        )
        image = await generate(html, ".container", True, segment=True)
        return image