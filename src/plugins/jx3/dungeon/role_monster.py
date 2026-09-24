from jinja2 import Template

from src.config import Config
from src.const.path import ASSETS, build_path
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.database.attributes import TabCache
from src.templates import SimpleHTML, get_saohua

from ._template import template_role_monsters

async def get_role_monsters_map(server: str, role_name: str):
    params = {
        "server": server,
        "name": role_name,
        "token": Config.jx3.api.token_v2
    }
    url = f"{Config.jx3.api.url}/monster/records"
    data = (await Request(url, params=params).get()).json()
    data = data["data"]
    content = []
    skill_list = sorted(
        data["skillList"],
        key=lambda skill: skill.get("nLevel", 0),
        reverse=True,
    )
    for skill in skill_list:
        icon_id, _ = TabCache.get_icon_for_skill(skill["dwInSkillID"])
        new = Template(template_role_monsters).render(
            icon = f"https://icon.jx3box.com/icon/{icon_id}.png",
            level = str(skill.get("nLevel", 0)),
            name = skill["szSkillName"]
        )
        content.append(new)
    html = str(
        SimpleHTML(
            "jx3",
            "role_monster.html",
            font = build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
            table_content = "\n".join(content),
            energy = data["skillEnergy"],
            stamina = data["skillStamina"],
            server = data["server"],
            name = data["roleName"],
            msg = get_saohua()
        )
    )
    image = await generate(html, ".report", segment=True)
    return image
