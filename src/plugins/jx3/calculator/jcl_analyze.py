from typing import Any, Literal
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
from src.utils.database.classes import CQCRank, THRRank

from ._template import (
    bla_template_body,

    fal_table_head,
    fal_template_body,
    
    yxc_table,
    hps_detail_template_body_main,
    hps_detail_template_body_sub,

    rod_table_head,
    rod_template_body,
    rod_css,

    asn_qte_table,
    asn_qte_template_body_main
)

def save_data(data: dict[str, dict[str, int | str]], value_type: bool, rank_key: Literal["THR", "CQC"]) -> None:
    """
    value_type(bool): `1/True` for dps, `0/False` for hps
    """
    if rank_key == "THR":
        rank_model = THRRank
    else:
        rank_model = CQCRank
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
        current_record: CQCRank | THRRank | Any = db.where_one(
            rank_model(),
            f"role_name = ? AND server_name = ? AND total_{key} = ?",
            role_name, server_name, to_judge_value,
            default=None
        )
        if current_record is not None:
            continue
        new_data = rank_model(
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
async def CQCAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
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
        save_data(data["data"][0], True, "CQC")
        save_data(data["data"][1], False, "CQC")
    except Exception:
        pass

    html = str(
        SimpleHTML(
            "jx3",
            "cqc_dps",
            title = "Inkar Suki 池清川P2战斗分析",
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
async def FALAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
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
async def YXCAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
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
            Template(hps_detail_template_body_main).render(
                icon=Kungfu.with_internel_id(int(each_record["kungfu_id"]), True).icon,
                name=player_name,
                value=each_record["value"]
            )
        )
        skills = dict(sorted(each_record["skills"].items(), key=lambda item: sum(item[1]), reverse=True))
        for skill_name, skill_values in skills.items():
            tables.append(
                Template(hps_detail_template_body_sub).render(
                    name = skill_name,
                    count = len(skill_values),
                    value = sum(skill_values),
                    percent = str(round(sum(skill_values) / each_record["value"] * 100, 2)) + "%"
                )
            )
    html = Template(
        read(TEMPLATES + "/jx3/health_detail.html")
    ).render(
        font = ASSETS + "/font/PingFangSC-Semibold.otf",
        tables = "\n".join(final_tables),
        saohua = get_saohua(),
        function_name = "尹雪尘承伤统计"
    )
    image = await generate(html, ".container", segment=True)
    return image

# Reason of Death
async def RODAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
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
async def HPSAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/hps_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()
    if data["data"] is None:
        return "分析失败，请检查 JCL 是否完整？如有必要请联系作者！"
    tables = []
    final_tables = []
    boss_name = data["data"]["boss"]
    for value_type in ["absorb", "health"]:
        for each_record in sort_dict_list(data["data"]["values"], f"total_{value_type}")[::-1]:
            if each_record[f"total_{value_type}"] == 0:
                continue
            tables.append(
                Template(hps_detail_template_body_main).render(
                    icon=Kungfu.with_internel_id(int(each_record["kungfu_id"]), True).icon,
                    name=each_record["name"],
                    value=str(each_record[f"total_{value_type}"]) + "<br>" + str(int(each_record[f"total_{value_type}"] / data["data"]["battle_time"])) + (" HPS" if value_type == "health" else " APS")
                )
            )
            skills = each_record["skills"][value_type]
            for skill in skills:
                tables.append(
                    Template(hps_detail_template_body_sub).render(
                        name = skill["name"],
                        count = str(skill["count"]) + "（" + str(skill["critical"]) + "会心）",
                        value = skill["value"],
                        percent = str(round(skill["value"] / each_record[f"total_{value_type}"] * 100, 2)) + "%"
                    )
                )
        final_tables.append(
            Template(yxc_table).render(
                tables = "\n".join(tables)
            )
        )
        tables = []
    html = Template(
        read(TEMPLATES + "/jx3/health_detail.html")
    ).render(
        font = ASSETS + "/font/PingFangSC-Semibold.otf",
        tables = "\n".join(final_tables),
        saohua = get_saohua(),
        function_name = f"{boss_name} HPS APS 统计"
    )
    image = await generate(html, ".container", segment=True)
    return image

async def CALAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.calculator_url}/submit_jcl", json={"url": url, "name": file_name, "user_id": user_id}, timeout=600)
        data = resp.json()
    if data["code"] != 200:
        if data["status"] == -1:
            return "请检查 JCL 名称，无法解析！\n参考格式：CAL-莫问-19285-紫武-常规循环.jcl\nCAL-心法名-加速等级-紫武/橙武-循环名.jcl"
        elif data["status"] == -2:
            return "请检查心法名称，无法识别该心法名称！"
    else:
        return "导入成功！\n发送「偏好 计算器来源 自定义」可使用导入的循环；\n发送「偏好 计算器来源 公用」可恢复使用公开循环！"

# A Shi Na (Cheng Qing)
async def ASNAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/asn_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()
    tables = []
    final_tables = []
    for each_round in data["data"]["hps"]:
        if each_round == {}:
            final_tables.append(
                Template(yxc_table).render(
                    tables = "\n".join(tables)
                )
            )
            tables = []
            continue
        player_name = each_round["name"]
        if anonymous:
            player_name = "匿名玩家"
        tables.append(
            Template(hps_detail_template_body_main).render(
                icon=Kungfu.with_internel_id(int(each_round["kungfu_id"]), True).icon,
                name=player_name,
                value=each_round["value"]
            )
        )
        skills = dict(sorted(each_round["skills"].items(), key=lambda item: sum(item[1]), reverse=True))
        for skill_name, skill_values in skills.items():
            tables.append(
                Template(hps_detail_template_body_sub).render(
                    name = skill_name,
                    count = len(skill_values),
                    value = sum(skill_values),
                    percent = str(round(sum(skill_values) / each_round["value"] * 100, 2)) + "%"
                )
            )
    html = Template(
        read(TEMPLATES + "/jx3/health_detail.html")
    ).render(
        font = ASSETS + "/font/PingFangSC-Semibold.otf",
        tables = "\n".join(final_tables),
        saohua = get_saohua(),
        function_name = "阿史那承庆 · 死侍期间治疗吸收盾 HPS 统计"
    )
    hps_image = await generate(html, ".container", segment=True)
    round_tables = []
    for each_round in data["data"]["hit"]:
        round_rows = []
        for player_name, values in dict(sorted(each_round.items(), key=lambda item: sum(item[1].values()), reverse=True)).items():
            if anonymous:
                player_name = "匿名玩家"
            round_rows.append(
                Template(asn_qte_template_body_main).render(
                    name=player_name,
                    good=values["good"],
                    bad=values["bad"]
                )
            )
        round_table = Template(asn_qte_table).render(
            tables="\n".join(round_rows)
        )
        round_tables.append(round_table)
    html = Template(
        read(TEMPLATES + "/jx3/health_detail.html")
    ).render(
        font=ASSETS + "/font/PingFangSC-Semibold.otf",
        tables="\n".join(round_tables),
        saohua=get_saohua(),
        function_name="阿史那承庆 · QTE 统计"
    )

    qte_image = await generate(html, ".container", segment=True)
    return hps_image + qte_image

# Tang Huai Ren
async def THRAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/thr_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()

    if data["code"] == 400:
        return "未识别到首领通关，请更换 JCL！"

    final_dps = []
    final_hps = []

    team_total_damage = sum(r["total_damage"] for r in data["data"][0].values())

    for player_name, player_data in data["data"][0].items():
        if anonymous:
            player_name = "匿名玩家"
        kungfu: Kungfu = Kungfu.with_internel_id(int(player_data["kungfu_id"]))
        single_record = Template(bla_template_body).render(
            icon = kungfu.icon,
            name = player_name + " - " + str(round(player_data["total_damage"] / team_total_damage * 100, 2)) + "%",
            rdps = "{:,}".format(int(player_data["total_damage"])),
            display = str(round(player_data["total_damage"] / list(data["data"][0].values())[0]["total_damage"], 4) * 100),
            color = kungfu.color,
            percent = "{:,}".format(int(player_data['damage_per_second']))
        )
        final_dps.append(
            single_record
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
                display = str(round(player_data["total_health"] / list(data["data"][1].values())[0]["total_health"] * 100, 2)),
                color = kungfu.color,
                percent = "{:,}".format(int(player_data['health_per_second']))
            )
        )
    try:
        save_data(data["data"][0], True, "THR")
        save_data(data["data"][1], False, "THR")
    except Exception:
        pass

    html = str(
        SimpleHTML(
            "jx3",
            "cqc_dps",
            title = "Inkar Suki 唐怀仁 P3 战斗统计",
            battle_time = data["battle_time"],
            dps_stastic = "\n".join(final_dps),
            hps_stastic = "\n".join(final_hps),
            saohua = get_saohua(),
            font = ASSETS + "/font/PingFangSC-Semibold.otf"
        )
    )
    dps_image = await generate(html, ".container", segment=True)
    return dps_image