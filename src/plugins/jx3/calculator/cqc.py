from typing import Any
from jinja2 import Template
from httpx import AsyncClient

from src.const.path import ASSETS
from src.const.jx3.kungfu import Kungfu
from src.utils.generate import generate
from src.templates import SimpleHTML, get_saohua

from src.utils.database import rank_db as db
from src.utils.database.classes import CQCRank

from ._template import template_rdps

def save_data(data: dict[str, dict[str, int | str]], value_type: bool) -> None:
    """
    value_type(bool): `1/True` for dps, `0/False` for hps
    """
    key = "damage" if value_type else "health"
    for role_full_name, role_data in data.items():
        role_name, server_name = role_full_name.split("·")
        kungfu_id = int(role_data["kungfu_id"])
        total_damage = 0
        total_health = 0
        damage_per_second = 0
        health_per_second = 0
        if value_type:
            total_damage = role_data[f"total_{key}"]
            damage_per_second = role_data[f"{key}_per_second"]
        else:
            total_health = role_data[f"total_{key}"]
            health_per_second = role_data[f"{key}_per_second"]
        to_judge_value = total_damage if value_type else total_health
        current_record: CQCRank | Any = db.where_one(
            CQCRank(),
            f"role_name = ? AND server_name = ? AND total_{key} = ?",
            role_name, server_name, to_judge_value,
            default=None
        )
        if current_record is not None:
            continue
        new_data = CQCRank(
            role_name = role_name,
            server_name = server_name,
            kungfu_id = kungfu_id
        )
        if value_type:
            setattr(new_data, f"total_{key}", total_damage)
            setattr(new_data, f"{key}_per_second", damage_per_second)
        else:
            setattr(new_data, f"total_{key}", total_health)
            setattr(new_data, f"{key}_per_second", health_per_second)
        db.save(new_data)
            

async def CQCAnalyze(file_name: str, url: str):
    async with AsyncClient(verify=False) as client:
        resp = await client.post("http://10.0.10.13:51511/cqc_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()

    final_dps = []
    final_hps = []

    for player_name, player_data in data["data"][0].items():
        kungfu: Kungfu = Kungfu.with_internel_id(int(player_data["kungfu_id"]))
        final_dps.append(
            Template(template_rdps).render(
                icon = kungfu.icon,
                name = player_name,
                rdps = "{:,}".format(int(player_data["total_damage"])),
                display = str(round(player_data["total_damage"] / list(data["data"][0].values())[0]["total_damage"], 4) * 100),
                color = kungfu.color,
                percent = "{:,}".format(int(player_data['damage_per_second']))
            )
        )

    for player_name, player_data in data["data"][1].items():
        kungfu: Kungfu = Kungfu.with_internel_id(int(player_data["kungfu_id"]))
        final_hps.append(
            Template(template_rdps.replace("dps-num", "hps-num")).render(
                icon = kungfu.icon,
                name = player_name,
                rdps = "{:,}".format(int(player_data["total_health"])),
                display = str(round(player_data["total_health"] / list(data["data"][1].values())[0]["total_health"], 4) * 100),
                color = kungfu.color,
                percent = "{:,}".format(int(player_data['health_per_second']))
            )
        )
    try:
        save_data(data["data"][0], True)
        save_data(data["data"][1], False)
    except Exception:
        pass

    html = str(
        SimpleHTML(
            "jx3",
            "cqc_dps",
            battle_time = data["battle_time"],
            dps_stastic = "\n".join(final_dps),
            hps_stastic = "\n".join(final_hps),
            saohua = get_saohua(),
            font = ASSETS + "/font/PingFangSC-Semibold.otf"
        )
    )
    dps_image = await generate(html, ".container", segment=True)
    return dps_image