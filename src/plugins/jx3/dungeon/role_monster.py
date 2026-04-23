from jinja2 import Template

from src.config import Config
from src.const.path import ASSETS, build_path
from src.utils.analyze import sort_dict_list
from src.utils.generate import generate
from src.utils.network import Request
from src.templates import SimpleHTML, get_saohua

from ._template import template_role_monsters

class BaizhanSkillNotRecognizedException(Exception): ...

class SkillMap:
    skill_data: list[dict] = []
    
    def __init__(self):
        ...
        
    @classmethod
    async def get_icon(cls, in_skill_id: int, out_skill_id: int) -> str:
        if not cls.skill_data:
            cls.skill_data = (await Request("https://node.jx3box.com/monster/skills").get()).json()["data"]["list"]
        for skill in cls.skill_data:
            if skill["dwInSkillID"] == in_skill_id and skill["dwOutSkillID"] == out_skill_id:
                return "https://icon.jx3box.com/icon/" + str(skill["Skill"]["IconID"]) + ".png"
        raise BaizhanSkillNotRecognizedException(f"Cannot recognize the baizhan skill `{in_skill_id}` and `{out_skill_id}`!")

async def get_role_monsters_map(server: str, role_name: str):
    params = {
        "server": server,
        "name": role_name,
        "token": Config.jx3.api.token_v2
    }
    url = f"{Config.jx3.api.url}/data/role/monster"
    data = (await Request(url, params=params).get()).json()
    data = data["data"]
    content = []
    skill_list = sort_dict_list(data["skill_list"], "skill_level")[::-1]
    for skill in skill_list:
        new = Template(template_role_monsters).render(
            icon = 1434, # JX3API 未返回图标
            level = str(skill["skill_level"]),
            name = skill["skill_name"]
        )
        content.append(new)
    html = str(
        SimpleHTML(
            "jx3",
            "role_monster.html",
            font = build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
            table_content = "\n".join(content),
            energy = data["skill_energy"],
            stamina = data["skill_stamina"],
            server = data["server"],
            name = data["role_name"],
            msg = get_saohua()
        )
    )
    image = await generate(html, "body", segment=True)
    return image