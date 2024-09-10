from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from jinja2 import Template

from src.tools.config import Config
from src.tools.basic.prompts import PROMPT
from src.tools.basic.server import server_mapping
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.generate import get_uuid, generate
from src.tools.utils.time import convert_time, get_relate_time, get_current_time
from src.tools.utils.file import read, write

from src.plugins.jx3.bind import get_player_local_data, Player

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

async def check_role(server: str, name: str) -> bool:
    player_data: Player = await get_player_local_data(role_name=name, server_name=server)
    if player_data.format_jx3api()["code"] != 200:
        return False
    return True

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
                    "image_path": ASSETS + "/serendipity/serendipity/" + path_map[int(serendipity["level"]) - 1] + "/" + serendipity["name"] + ".png",
                    "name": serendipity["name"],
                    "status": "yes" if status else "no",
                    "msg": "尚未触发" if not status else "遗忘的时间" if corresponding["time"] == 0 else convert_time(corresponding["time"], "%Y-%m-%d %H:%M:%S") + "<br>" + get_relate_time(get_current_time(), corresponding["time"])
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

async def get_serendipity_image_v3(server: Optional[str], name: str, group_id: Optional[str] = ""):
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT.ServerNotExist]
    player_exist = await check_role(server, name)
    if not player_exist:
        return [PROMPT.PlayerNotExist]

    data: list = await JX3Serendipity().integration(server, name)
    data_obj = JX3Serendipities(data)

    common: List[dict] = data_obj.common
    peerless: List[dict] = data_obj.peerless
    pet: List[dict] = data_obj.pet

    local_common: List[dict] = [{"name": serendipity[:-4], "level": 1} for serendipity in os.listdir(ASSETS + "/serendipity/serendipity/common/")]
    local_peerless: List[dict] = [{"name": serendipity[:-4], "level": 2} for serendipity in os.listdir(ASSETS + "/serendipity/serendipity/peerless/")]
    local_pet: List[dict] = [{"name": serendipity[:-4], "level": 3} for serendipity in os.listdir(ASSETS + "/serendipity/serendipity/pet/")]
    
    path_map: List[str] = ["common", "peerless", "pet"]
 
    common_table = generate_table(local_common, common, path_map, template)
    peerless_table = generate_table(local_peerless, peerless, path_map, template)
    pet_table = generate_table(local_pet, pet, path_map, template)

    font = ASSETS + "/font/custom.ttf"
    html = read(VIEWS + "/jx3/serendipity/v3.html")
    html = Template(html).render(
        **{
            "font": font,
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
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()
