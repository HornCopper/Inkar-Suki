from typing import Any
from jinja2 import Template
from httpx import AsyncClient

from src.config import Config
from src.const.path import ASSETS, TEMPLATES
from src.const.jx3.kungfu import Kungfu
from src.utils.file import read
from src.utils.analyze import sort_dict_list
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import SimpleHTML, HTMLSourceCode, get_saohua

from src.utils.database import rank_db as db
from src.utils.database.classes import CQCRank

from ._template import bla_template_body, fal_table_head, fal_template_body, yxc_table_head, yxc_template_body_main, yxc_template_body_sub

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
        resp = await client.post(f"{Config.jx3.api.cqc_url}/cqc_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()

    final_dps = []
    final_hps = []

    for player_name, player_data in data["data"][0].items():
        kungfu: Kungfu = Kungfu.with_internel_id(int(player_data["kungfu_id"]))
        final_dps.append(
            Template(bla_template_body).render(
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
            Template(bla_template_body.replace("dps-num", "hps-num")).render(
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

async def FALAnalyze(file_name: str, url: str):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/fal_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()
    tables = []
    for each_record in data["data"]:
        tables.append(
            Template(fal_template_body).render(
                time = Time(each_record["time"]).format("%H:%M:%S"),
                releaser = each_record["releaser_name"] + "<br>（" + str(each_record["releaser_id"]) + "）",
                target = each_record["target_name"] + "<br>（" + str(each_record["target_id"]) + "/" + str(each_record["target_template_id"]) + "）",
                skill = str(each_record["skill_id"])
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = "开怪统计",
            table_head = fal_table_head,
            table_body = "\n".join(tables)
        )
    )
    image = await generate(html, ".container", segment=True)
    return image  

async def YXCAnalyze(file_name: str, url: str):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/yxc_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()
    tables = []
    for each_record in data["data"]:
        tables.append(
            Template(yxc_template_body_main).render(
                icon=Kungfu.with_internel_id(int(each_record["kungfu_id"]), True).icon,
                name=each_record["name"],
                value=each_record["value"]
            )
        )
        skills = dict(sorted(each_record["skills"].items(), key=lambda item: sum(item[1]), reverse=True))
        for skill_name, skill_values in skills.items():
            tables.append(
                Template(yxc_template_body_sub).render(
                    name = skill_name,
                    count = len(skill_values),
                    value = sum(skill_values),
                    percent = str(round(sum(skill_values) / each_record["value"] * 100, 2)) + "%"
                )
            )
    html = Template(
        read(TEMPLATES + "/jx3/yxc_chps.html")
    ).render(
        font = ASSETS + "/font/PingFangSC-Semibold.otf",
        tables = "\n".join(tables),
        saohua = get_saohua()
    )
    image = await generate(html, ".container", segment=True)
    return image  

async def HPSAnalyze(file_name: str, url: str):
    ...