from typing import Any
from jinja2 import Template
from httpx import AsyncClient

from src.const.path import ASSETS
from src.const.jx3.kungfu import Kungfu
from src.utils.generate import generate
from src.templates import SimpleHTML, get_saohua

from ._template import template_rdps

import re

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