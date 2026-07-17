from jinja2 import Template

from src.config import Config
from src.const.path import ASSETS
from src.const.jx3.kungfu import Kungfu
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.database.attributes import TabCache
from src.utils.database.constant import Colors
from src.templates import SimpleHTML, get_saohua

from ._template import (
    battle_rank_template_body,
    hps_template_img_talent,
    hps_template_img_weapon,
)


async def get_battle_rank(kungfu_name: str, boss_name: str):
    rank_type = kungfu_name.upper()
    if rank_type in {"DPS", "HPS"}:
        kungfu_id = 0
        is_healer = rank_type == "HPS"
    else:
        kungfu = Kungfu(kungfu_name)
        kungfu_id = kungfu.id
        if kungfu_id is None:
            return "未找到该心法，请检查后重试！"
        is_healer = kungfu.abbr == "N"
    endpoint = "hps_rank" if is_healer else "dps_rank"
    primary_name = "HPS" if is_healer else "DPS"
    params = {"boss_name": boss_name, "kungfu_id": kungfu_id}
    data = (
        await Request(f"{Config.jx3.api.cqc_url}/{endpoint}", params=params).get()
    ).json()
    if data["code"] != 200:
        return "获取榜单失败！"
    if data["results"] == []:
        return "当前首领尚未被上传数据，或首领不存在。"
    tables = []
    rank_num = 0
    for each_record in data["results"]:
        rank_num += 1
        battle_time = each_record["battle_time"]
        talents = []
        for each_talent in each_record["key_talents"]:
            icon_id, name = TabCache.get_icon_for_skill(each_talent)
            talents.append(
                Template(hps_template_img_talent).render(
                    icon=f"https://icon.jx3box.com/icon/{icon_id}.png",
                    name=name,
                )
            )
        weapon_id = each_record["weapon_id"]
        weapon_info = ""
        if weapon_id != 0:
            weapon_data = TabCache.get_equip(weapon_id, 3)
            ui_id = weapon_data[2]
            icon_id, name = TabCache.get_icon_for_equip(ui_id)
            color = "rgb" + Colors[int(weapon_data[22])]
            quality = int(weapon_data[12])
            weapon_info = Template(hps_template_img_weapon).render(
                color=color,
                icon=f"https://icon.jx3box.com/icon/{icon_id}.png",
                name=name,
                quality=quality
            )
        if is_healer:
            primary_value = int(each_record["total_health"] / battle_time)
        else:
            primary_value = int(each_record["total_damage"] / battle_time)
        tables.append(
            Template(battle_rank_template_body).render(
                kungfu_icon=Kungfu.with_internel_id(each_record["kungfu_id"]).icon,
                rank_num=rank_num,
                role_name=each_record["role_name"],
                role_server=each_record["server_name"],
                primary_value="{:,}".format(primary_value),
                time_cost=f"{battle_time // 60}:{battle_time % 60}",
                talents="\n".join(talents),
                weapon=weapon_info,
            )
        )
    html = str(
        SimpleHTML(
            "jx3",
            "hps_rank",
            font=ASSETS + "/font/PingFangSC-Semibold.otf",
            table="\n".join(tables),
            boss_name=boss_name,
            primary_name=primary_name,
            saohua=get_saohua(),
        )
    )
    image = await generate(html, ".container", segment=True)
    return image
