from pathlib import Path
from typing import Literal
from jinja2 import Template

from src.const.prompts import PROMPT
from src.const.path import ASSETS, build_path
from src.utils.generate import generate
from src.utils.time import Time
from src.utils.database.player import search_player, Player
from src.templates import SimpleHTML

from .without_jx3api import JX3Serendipity

import os

template: str = """
<td class="element-column">
    <div class="element-container">
        <img class="{{ status }}-color" src="{{ image_path }}" alt="{{ name }}.png">
        <div class="{{ status }}-serendipity">{{ msg }}</div>
    </div>
</td>"""

class JX3Serendipities:
    def __init__(self, data: list):
        self.data = data
        

    @property
    def common(self):
        new = []
        for serendipity in self.data:
            if serendipity["level"] == 1:
                new.append(serendipity)
        return new
    
    @property
    def pet(self):
        new = []
        for serendipity in self.data:
            if serendipity["level"] == 3:
                new.append(serendipity)
        return new

    @property
    def peerless(self):
        new = []
        for serendipity in self.data:
            if serendipity["level"] == 2:
                new.append(serendipity)
        return new

async def check_role(server: str, name: str) -> Literal[False] | str:
    player_data: Player = await search_player(role_name=name, server_name=server)
    if player_data.format_jx3api()["code"] != 200:
        return False
    return player_data.format_jx3api()["data"]["roleId"]

def generate_table(local_data, comparison_data, path_map, template):
    table_list = []
    cache_table = []
    
    for serendipity in local_data:
        status = serendipity["name"] in [item["name"] for item in comparison_data]
        corresponding = {}
        for item in comparison_data:
            if item["name"] == serendipity["name"]:
                corresponding = item

        cache_table.append(
            Template(template).render(
                **{
                    "image_path": build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", path_map[int(serendipity["level"]) - 1]], end_with_slash=True) + serendipity["name"] + ".png",
                    "name": serendipity["name"],
                    "status": "yes" if status else "no",
                    "msg": "尚未触发" if not status else "遗忘的时间" if corresponding["time"] == 0 else Time(corresponding["time"]).format("%Y-%m-%d %H:%M:%S") + "<br>" + Time().relate(corresponding["time"])
                }
            )
        )

        if len(cache_table) == 5:
            table_list.append(
                "<tr>\n" + "\n".join(cache_table) + "\n</tr>"
            )
            cache_table = []

    if len(cache_table) != 0:
        table_list.append(
            "<tr>\n" + "\n".join(cache_table) + "\n</tr>"
        )
    return table_list

async def get_serendipity_image_v3(server: str, name: str):
    uid = await check_role(server, name)
    if not uid:
        return PROMPT.PlayerNotExist

    data: list = await JX3Serendipity().integration(server, name, uid)
    data_obj = JX3Serendipities(data)

    common: list[dict] = data_obj.common
    peerless: list[dict] = data_obj.peerless
    pet: list[dict] = data_obj.pet

    local_common: list[dict] = [{"name": serendipity[:-4], "level": 1} for serendipity in os.listdir(build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", "common"], end_with_slash=True))]
    local_peerless: list[dict] = [{"name": serendipity[:-4], "level": 2} for serendipity in os.listdir(build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", "peerless"], end_with_slash=True))]
    local_pet: list[dict] = [{"name": serendipity[:-4], "level": 3} for serendipity in os.listdir(build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", "pet"], end_with_slash=True))]
    
    path_map: list[str] = ["common", "peerless", "pet"]
 
    common_table = generate_table(local_common, common, path_map, template)
    peerless_table = generate_table(local_peerless, peerless, path_map, template)
    pet_table = generate_table(local_pet, pet, path_map, template)

    html = str(
        SimpleHTML(
            "jx3",
            "serendipity_v3",
            **{
            "font": build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
            "name": name,
            "server": server,
            "total": f"{len(data)}/{len(local_common + local_peerless + local_pet)}",
            "peerless": len(peerless),
            "pet": len(pet),
            "table_content_peerless": "\n".join(peerless_table),
            "table_content_common": "\n".join(common_table),
            "table_content_pet": "\n".join(pet_table)
        }
        )
    )
    image = await generate(html, ".total", segment=True)
    return image