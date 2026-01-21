from typing import Any
from jinja2 import Template
from httpx import AsyncClient

from src.config import Config
from src.const.path import ASSETS
from src.const.jx3.kungfu import Kungfu
from src.const.jx3.school import School
from src.utils.analyze import check_number, sort_dict_list
from src.utils.generate import generate
from src.templates import SimpleHTML, get_saohua

from ._template import bla_template_body

import re

async def RDPSCalculator(file_name: str, url: str, anonymous: bool = False):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.bla_url}/jcl", params={"file_name": file_name, "url": url}, timeout=600)
        data = resp.json()
    pattern = r"^\d{4}(?:-\d{2}){5}-(?P<dungeon>.+?)\(\d+\)-(?P<boss>.+?)\(\d+\)\.jcl$"
    regex_match = re.match(pattern, file_name)
    dungeon, boss = regex_match.group("dungeon"), regex_match.group("boss") #type: ignore

    rdps_data = data["rdps"]
    total_rdps = "{:,}".format(int(rdps_data["sum"]))

    rhps_data = data["rhps"]
    total_rhps = "{:,}".format(int(rhps_data["sum"]))

    rdps_player_data: dict[str, dict[str, Any]] = rdps_data["player"]
    rdps_results: list[dict[str, str | int | Kungfu | None]] = []

    rhps_player_data: dict[str, dict[str, Any]] = rhps_data["player"]
    rhps_results: list[dict[str, str | int | Kungfu | None]] = []

    for name, p_data in rdps_player_data.items():
        if not check_number(name):
            # 非玩家RDPS
            rdps_results.append(
                {
                    "name": name,
                    "rdps": int(p_data["dps"]),
                    "kungfu": None
                }
            )
        else:
            # 玩家RDPS
            kungfu_id = p_data["occ"]
            if check_number(kungfu_id):
                # 单心法职业
                kungfu = Kungfu(
                    School.with_internel_id(int(kungfu_id)).name
                )
            else:
                t = ""
                keyword = kungfu_id[-1]
                force_id = kungfu_id[:-1]
                if keyword == "w":
                    keyword = kungfu_id[-2]
                    force_id = kungfu_id[:-2]
                if keyword == "h":
                    t = "HPS"
                if keyword == "t":
                    t = "T"
                if keyword == "d":
                    t = "DPS"
                if keyword == "m":
                    if force_id == "4":
                        t = "QC"
                    else:
                        t = "TL"
                if keyword == "p":
                    if force_id == "4":
                        t = "JC"
                    else:
                        t = "JY"
                kungfu = Kungfu(
                    str(School.with_internel_id(int(force_id)).name) + t
                )
            player_name = p_data["name"]
            if anonymous:
                player_name = "匿名玩家"
            rdps_results.append(
                {
                    "name": player_name,
                    "rdps": int(p_data["dps"]),
                    "kungfu": kungfu
                }
            )
    
    for name, p_data in rhps_player_data.items():
        if not check_number(name):
            # 非玩家RDPS
            rhps_results.append(
                {
                    "name": name,
                    "rhps": int(p_data["hps"]),
                    "kungfu": None
                }
            )
        else:
            # 玩家RDPS
            kungfu_id = p_data["occ"]
            if check_number(kungfu_id):
                # 单心法职业
                kungfu = Kungfu(
                    School.with_internel_id(int(kungfu_id)).name
                )
            else:
                t = ""
                keyword = kungfu_id[-1]
                force_id = kungfu_id[:-1]
                if keyword == "w":
                    keyword = kungfu_id[-2]
                    force_id = kungfu_id[:-2]
                if keyword == "h":
                    t = "HPS"
                if keyword == "t":
                    t = "T"
                if keyword == "d":
                    t = "DPS"
                if keyword == "m":
                    if force_id == "4":
                        t = "QC"
                    else:
                        t = "TL"
                if keyword == "p":
                    if force_id == "4":
                        t = "JC"
                    else:
                        t = "JY"
                kungfu = Kungfu(
                    str(School.with_internel_id(int(force_id)).name) + t
                )
            player_name = p_data["name"]
            if anonymous:
                player_name = "匿名玩家"
            rhps_results.append(
                {
                    "name": player_name,
                    "rhps": int(p_data["hps"]),
                    "kungfu": kungfu
                }
            )

    final_rdps = []
    final_rhps = []

    rdps_final_results = sort_dict_list(rdps_results, "rdps")[::-1]
    rhps_final_results = sort_dict_list(rhps_results, "rhps")[::-1]
    
    rd_rank = 1
    rh_rank = 1

    for each_rdps in rdps_final_results:
        if each_rdps["kungfu"] is None:
            final_rdps.append(
                Template(bla_template_body).render(
                    icon = Kungfu(None).icon,
                    name = each_rdps["name"],
                    rdps = "{:,}".format(int(each_rdps["rdps"])),
                    display = str(round(each_rdps["rdps"] / rdps_final_results[0]["rdps"], 4) * 100),
                    color = "#000000",
                    percent = str(round(int(each_rdps["rdps"]) / int(rdps_data["sum"]) * 100, 2)) + "%"
                )
            )
        else:
            kungfu: Kungfu = each_rdps["kungfu"]
            final_rdps.append(
                Template(bla_template_body).render(
                    icon = kungfu.icon,
                    name = f"#{rd_rank} " + each_rdps["name"],
                    rdps = "{:,}".format(int(each_rdps["rdps"])),
                    display = str(round(each_rdps["rdps"] / rdps_final_results[0]["rdps"], 4) * 100),
                    color = kungfu.color,
                    percent = str(round(int(each_rdps["rdps"]) / int(rdps_data["sum"]) * 100, 2)) + "%"
                )
            )
            rd_rank += 1

    for each_rhps in rhps_final_results:
        if each_rhps["kungfu"] is None:
            final_rhps.append(
                Template(bla_template_body).render(
                    icon = Kungfu(None).icon,
                    name = each_rhps["name"],
                    rdps = "{:,}".format(int(each_rhps["rhps"])),
                    display = str(round(each_rhps["rhps"] / rhps_final_results[0]["rhps"], 4) * 100),
                    color = "#000000",
                    percent = str(round(int(each_rhps["rhps"]) / int(rhps_data["sum"]) * 100, 2)) + "%"
                )
            )
        else:
            kungfu: Kungfu = each_rhps["kungfu"]
            final_rhps.append(
                Template(bla_template_body).render(
                    icon = kungfu.icon,
                    name = f"#{rh_rank} " + each_rhps["name"],
                    rdps = "{:,}".format(int(each_rhps["rhps"])),
                    display = str(round(each_rhps["rhps"] / rhps_final_results[0]["rhps"], 4) * 100),
                    color = kungfu.color,
                    percent = str(round(int(each_rhps["rhps"]) / int(rhps_data["sum"]) * 100, 2)) + "%"
                )
            )
            rh_rank += 1

    html = str(
        SimpleHTML(
            "jx3",
            "rdps",
            dungeon = dungeon,
            boss = boss,
            rdps = total_rdps,
            rdps_players = "\n".join(final_rdps),
            saohua = get_saohua(),
            font = ASSETS + "/font/PingFangSC-Semibold.otf"
        )
    )
    rdps_image = await generate(html, ".container", segment=True)
    html = str(
        SimpleHTML(
            "jx3",
            "rhps",
            dungeon = dungeon,
            boss = boss,
            rhps = total_rhps,
            rhps_players = "\n".join(final_rhps),
            saohua = get_saohua(),
            font = ASSETS + "/font/PingFangSC-Semibold.otf"
        )
    )
    rhps_image = await generate(html, ".container", segment=True)
    return rdps_image + rhps_image