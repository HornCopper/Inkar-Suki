from typing import Any, Literal
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

def _normalize_merged_jcl_analysis(data: dict[str, Any]) -> dict[str, Any]:
    rdps_players: dict[str, dict[str, Any]] = {}
    for index, player in enumerate(data.get("stat", [])):
        rdps = int(player.get("rdps") or 0)
        if rdps <= 0:
            continue
        player_key = str(index)
        rdps_players[player_key] = {
            "name": player.get("name", player_key),
            "occ": str(player.get("occ", "")),
            "dps": rdps,
        }

    rhps_players: dict[str, dict[str, Any]] = {}
    for index, (name, player) in enumerate(data.get("occResult", {}).items()):
        result = player.get("result", {})
        healer = result.get("skill", {}).get("healer", {})
        rhps = int(healer.get("rhps") or result.get("dps", {}).get("stat", {}).get("rhps") or 0)
        if rhps <= 0:
            continue
        player_name = result.get("overall", {}).get("name") or name
        rhps_players[str(index)] = {
            "name": player_name,
            "occ": str(player.get("occ", "")),
            "hps": rhps,
        }

    return {
        "rdps": {
            "sum": sum(player["dps"] for player in rdps_players.values()),
            "player": rdps_players,
        },
        "rhps": {
            "sum": sum(player["hps"] for player in rhps_players.values()),
            "player": rhps_players,
        },
    }


def _normalize_bla_analysis(data: dict[str, Any]) -> dict[str, Any]:
    if "rdps" in data and "rhps" in data:
        return data
    if "stat" in data and "occResult" in data:
        return _normalize_merged_jcl_analysis(data)
    raise KeyError("Unsupported BLA analysis response")

async def BLACalculator(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    return await BLACalculate(file_name, url, anonymous, "default")

async def TRDCalculator(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    return await BLACalculate(file_name, url, anonymous, "thr_p1")

async def BLACalculate(file_name: str, url: str, anonymous: bool = False, analyze_type: Literal["default", "thr_p1"] = "default"):
    if analyze_type == "thr_p1":
        url_path = "jcl_thr_p1"
    else:
        url_path = "jcl"
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.bla_url}/{url_path}", params={"file_name": file_name, "url": url}, timeout=600)
        raw_data = resp.json()
        data = _normalize_bla_analysis(raw_data)
    pattern = r"^\d{4}(?:-\d{2}){5}-(?P<dungeon>.+?)\(\d+\)-(?P<boss>.+?)\(\d+\)\.jcl$"
    regex_match = re.match(pattern, file_name)
    dungeon, boss = regex_match.group("dungeon"), regex_match.group("boss") #type: ignore
    boss = raw_data.get("overall", {}).get("boss") or boss
    if analyze_type == "thr_p1":
        boss = boss + "【仅第一阶段】"

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
