from pathlib import Path
from typing import Literal
from time import time
from jinja2 import Template

from src.config import Config
from src.const.prompts import PROMPT
from src.const.path import ASSETS, build_path
from src.const.jx3.school import School
from src.utils.generate import generate
from src.utils.time import Time
from src.utils.network import Request
from src.utils.database.player import search_player
from src.templates import SimpleHTML
from src.utils.analyze import sort_dict_list

from ._template import template_v3_cell, template_v3_row
from .without_jx3api import JX3Serendipity

import os

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

async def check_role(
    server: str, name: str
) -> Literal[False] | tuple[str, str, str]:
    player_data = await search_player(role_name=name, server_name=server)
    role_id = player_data.roleId
    if role_id == "":
        return False
    return (
        role_id,
        player_data.globalRoleId,
        School(player_data.forceName).name or player_data.forceName,
    )

def _featured_image_path(name: str, category: str, school: str) -> str:
    directory = build_path(
        ASSETS,
        ["image", "jx3", "serendipity", "show", category],
        end_with_slash=True,
    )
    for asset_name in (name, f"{name}-{school}"):
        path = directory + asset_name + ".png"
        if Path(path).exists():
            return path
    return ""


def _featured_name_path(name: str, level: int) -> str:
    directory = build_path(
        ASSETS, ["image", "jx3", "serendipity", "name"], end_with_slash=True
    )
    name_path = directory + name + ".png"
    if Path(name_path).exists():
        return name_path
    if level == 3:
        return directory + "宠物奇缘.png"
    return ""


def generate_table(
    local_data: list[dict],
    comparison_data: list[dict],
    path_map: list[str],
    template: str,
    school: str = "",
):
    local_dict = {item["name"]: item for item in local_data}
    comparison_data = sort_dict_list(comparison_data, "time")[::-1]
    handled_names = set()
    record_times = {}
    cell_data = []

    for item in comparison_data:
        name = item["event"] if Config.jx3.api.enable else item["name"]
        handled_names.add(name)
        record_times[name] = int(item["time"] or 0)
        serendipity = local_dict.get(name)
        status = serendipity is not None

        if status:
            level = int(serendipity["level"])
            image_path = build_path(
                ASSETS,
                ["image", "jx3", "serendipity", "serendipity", path_map[level - 1]],
                end_with_slash=True
            ) + name + ".png"
        else:
            image_path = ""

        msg = "尚未触发"
        if item["time"] != 0:
            msg = Time(item["time"]).format("%Y-%m-%d %H:%M:%S") + "<br>" + Time().relate(item["time"])
        elif status:
            msg = "遗忘的时间"

        cell_data.append((name, serendipity, image_path, "yes" if status else "no", msg))

    for name, serendipity in local_dict.items():
        if name in handled_names:
            continue

        level = int(serendipity["level"])
        image_path = build_path(
            ASSETS,
            ["image", "jx3", "serendipity", "serendipity", path_map[level - 1]],
            end_with_slash=True
        ) + name + ".png"

        cell_data.append((name, serendipity, image_path, "no", "尚未触发"))

    # The featured card needs both the scene and the rendered name. Keep the
    # newest usable entry at the head so every section can retain its fixed
    # two-row ink-circle slot even when the newest record lacks an asset.
    now = int(time())
    featured_candidates = sorted(
        (
            (index, cell)
            for index, cell in enumerate(cell_data)
            if cell[3] == "yes" and record_times.get(cell[0], 0) > 0
        ),
        key=lambda candidate: abs(record_times[candidate[1][0]] - now),
    )
    for index, (name, serendipity, _, _, _) in featured_candidates:
        level = int(serendipity["level"]) if serendipity else 1
        show_path = _featured_image_path(name, path_map[level - 1], school)
        name_path = _featured_name_path(name, level)
        if show_path and name_path:
            if index:
                cell_data.insert(0, cell_data.pop(index))
            break

    rendered_cells = []
    has_featured = False
    for index, (name, serendipity, image_path, status, msg) in enumerate(cell_data):
        level = int(serendipity["level"]) if serendipity else 1
        show_path = _featured_image_path(name, path_map[level - 1], school)
        name_path = _featured_name_path(name, level)
        featured_image_path = ""
        if index == 0 and status == "yes" and show_path and name_path:
            featured_image_path = show_path
            has_featured = True

        rendered_cells.append(
            Template(template).render(
                image_path=image_path,
                featured_image_path=featured_image_path,
                featured_name_path=name_path,
                serendipity_icon=build_path(
                    ASSETS, ["image", "jx3", "serendipity", "vector", "icon.png"]
                ),
                name=name,
                category=path_map[level - 1],
                status=status,
                msg=msg
            )
        )

    table_list = []
    offset = 0
    if has_featured:
        table_list.append(Template(template_v3_row).render(cells="\n".join(rendered_cells[:5])))
        table_list.append(Template(template_v3_row).render(cells="\n".join(rendered_cells[5:9])))
        offset = 9

    for index in range(offset, len(rendered_cells), 5):
        table_list.append(
            Template(template_v3_row).render(cells="\n".join(rendered_cells[index:index + 5]))
        )

    return table_list

async def get_serendipity_image_v3(server: str, name: str):
    role = await check_role(server, name)
    if not role:
        return PROMPT.PlayerNotExist
    uid, global_role_id, school = role

    if Config.jx3.api.enable:
        url = f"{Config.jx3.api.url}/data/event/records"
        params = {
            "server": server,
            "name": name,
            "token": Config.jx3.api.token
        }
        serendipity_data = (await Request(url, params=params).get()).json()
        data: list[dict] = await JX3Serendipity().merge_api_with_my_data(
            serendipity_data["data"], server, name, global_role_id, uid
        )
    else:
        data: list[dict] = await JX3Serendipity().integration(
            server, name, uid, global_role_id
        )
    data_obj = JX3Serendipities(data)

    common: list[dict] = data_obj.common
    peerless: list[dict] = data_obj.peerless
    pet: list[dict] = data_obj.pet

    local_common: list[dict] = [{"name": serendipity[:-4], "level": 1} for serendipity in os.listdir(build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", "common"], end_with_slash=True))]
    local_peerless: list[dict] = [{"name": serendipity[:-4], "level": 2} for serendipity in os.listdir(build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", "peerless"], end_with_slash=True))]
    local_pet: list[dict] = [{"name": serendipity[:-4], "level": 3} for serendipity in os.listdir(build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", "pet"], end_with_slash=True))]
    
    path_map: list[str] = ["common", "peerless", "pet"]
 
    common_table = generate_table(local_common, common, path_map, template_v3_cell, school)
    peerless_table = generate_table(local_peerless, peerless, path_map, template_v3_cell, school)
    pet_table = generate_table(local_pet, pet, path_map, template_v3_cell, school)

    html = str(
        SimpleHTML(
            "jx3",
            "serendipity_v3",
            **{
            "font": build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
            "ink_background": build_path(ASSETS, ["image", "jx3", "serendipity", "vector", "background.png"]),
            "name": name,
            "server": server,
            "total": f"{len(data)}/{len(local_common + local_peerless + local_pet)}",
            "peerless": len(peerless),
            "pet": len(pet),
            "app_info": f"个人奇遇记录 · {server} · {name} · " + Time().format("%H:%M:%S"),
            "table_content_peerless": "\n".join(peerless_table),
            "table_content_common": "\n".join(common_table),
            "table_content_pet": "\n".join(pet_table)
        }
        )
    )
    image = await generate(html, ".total", segment=True)
    return image
