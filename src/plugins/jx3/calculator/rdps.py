from typing import Any
from jinja2 import Template
from httpx import AsyncClient

from src.const.path import ASSETS
from src.const.jx3.kungfu import Kungfu
from src.const.jx3.school import School
from src.utils.analyze import check_number, sort_dict_list
from src.utils.generate import generate
from src.templates import SimpleHTML, get_saohua

from ._template import template_rdps

async def RDPSCalculator(file_name: str, url: str):
    async with AsyncClient(verify=False) as client:
        resp = await client.post("http://10.0.10.13:30172/jcl", params={"file_name": file_name, "url": url}, timeout=90)
        data = resp.json()
    rdps_data = data["rdps"]
    total_rdps = "{:,}".format(int(rdps_data["sum"]))
    player_data: dict[str, dict[str, Any]] = rdps_data["player"]
    results: list[dict[str, str | int | Kungfu | None]] = []
    for name, p_data in player_data.items():
        if not check_number(name):
            # 非玩家RDPS
            results.append(
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
                keyword = kungfu_id[-1]
                force_id = kungfu_id[:-1]
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
            results.append(
                {
                    "name": p_data["name"],
                    "rdps": int(p_data["dps"]),
                    "kungfu": kungfu
                }
            )
    final_rdps = []
    final_results = sort_dict_list(results, "rdps")[::-1]
    for each_rdps in final_results:
        if each_rdps["kungfu"] is None:
            final_rdps.append(
                Template(template_rdps).render(
                    icon = Kungfu(None).icon,
                    name = each_rdps["name"],
                    rdps = "{:,}".format(int(each_rdps["rdps"])),
                    display = str(round(each_rdps["rdps"] / final_results[0]["rdps"], 4) * 100),
                    color = "#000000"
                )
            )
        else:
            kungfu: Kungfu = each_rdps["kungfu"]
            final_rdps.append(
                Template(template_rdps).render(
                    icon = kungfu.icon,
                    name = each_rdps["name"],
                    rdps = "{:,}".format(int(each_rdps["rdps"])),
                    display = str(round(each_rdps["rdps"] / final_results[0]["rdps"], 4) * 100),
                    color = kungfu.color
                )
            )
    html = str(
        SimpleHTML(
            "jx3",
            "rdps",
            rdps = total_rdps,
            players = "\n".join(final_rdps),
            saohua = get_saohua(),
            font = ASSETS + "/font/PingFangSC-Semibold.otf"
        )
    )
    return await generate(html, ".container", segment=True)