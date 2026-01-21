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

from ._template import (
    bla_template_body,
    fal_table_head,
    fal_template_body,
    
    yxc_table,
    yxc_table_head,
    yxc_template_body_main,
    yxc_template_body_sub,

    rod_table_head,
    rod_template_body,
    rod_css
)

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
            
# Chi Qing Chuan
async def CQCAnalyze(file_name: str, url: str, anonymous: bool = False):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/cqc_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()

    final_dps = []
    final_hps = []

    for player_name, player_data in data["data"][0].items():
        if anonymous:
            player_name = "匿名玩家"
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
        if anonymous:
            player_name = "匿名玩家"
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

# First Attacking List
async def FALAnalyze(file_name: str, url: str, anonymous: bool = False):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/fal_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()
    tables = []
    for each_record in data["data"]:
        releaser_name = each_record["releaser_name"]
        # if anonymous:
        #     releaser_name = "匿名玩家"
        tables.append(
            Template(fal_template_body).render(
                time = Time(each_record["time"]).format("%H:%M:%S"),
                releaser = releaser_name + "<br>（" + str(each_record["releaser_id"]) + "）",
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

# Yin Xue Chen
async def YXCAnalyze(file_name: str, url: str, anonymous: bool = False):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/yxc_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()
    tables = []
    final_tables = []
    for each_record in data["data"]:
        if each_record == {}:
            final_tables.append(
                Template(yxc_table).render(
                    tables = "\n".join(tables)
                )
            )
            tables = []
            continue
        player_name = each_record["name"]
        if anonymous:
            player_name = "匿名玩家"
        tables.append(
            Template(yxc_template_body_main).render(
                icon=Kungfu.with_internel_id(int(each_record["kungfu_id"]), True).icon,
                name=player_name,
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
        tables = "\n".join(final_tables),
        saohua = get_saohua()
    )
    image = await generate(html, ".container", segment=True)
    return image

# Reason of Death
async def RODAnalyze(file_name: str, url: str, anonymous: bool = False):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/rod_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()
    tables = []
    for each_record in data["data"]:
        # if anonymous:
        #     releaser_name = "匿名玩家"
        remark = ""
        skills = []
        for each_skill in each_record["final_damages"]:
            time = Time(each_skill["time"]).format("%H:%M:%S")
            name = each_skill["name"]
            damage = each_skill["effective_damage"]
            skills.append(
                f"[{time}]<span style=\"text-decoration: underline;\">{name}</span>：{damage}"
            )
        tables.append(
            Template(rod_template_body).render(
                time = Time(each_record["time"]).format("%H:%M:%S"),
                icon = Kungfu.with_internel_id(each_record["kungfu_id"], True).icon,
                name = each_record["name"],
                skills = ("<br>".join(skills) or "好像没有吃技能呢？<br>可能是战斗开始前死亡或者杯水到期等。"),
                remark = remark
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = "重伤统计",
            table_head = rod_table_head,
            table_body = "\n".join(tables),
            additional_css=rod_css
        )
    )
    image = await generate(html, ".container", segment=True)
    return image

# Healing per Second
async def HPSAnalyze(file_name: str, url: str, anonymous: bool = False):
    ...