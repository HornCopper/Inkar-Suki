from pathlib import Path
from jinja2 import Template

from src.const.prompts import PROMPT
from src.const.jx3.kungfu import Kungfu
from src.const.path import ASSETS, TEMPLATES, SHOW, build_path
from src.utils.file import read
from src.utils.network import cache_image
from src.utils.database.player import search_player
from src.utils.generate import generate
from src.templates import get_saohua
from src.utils.database.attributes import Equip, JX3PlayerAttribute, split_display_attributes
from src.plugins.jx3.calculator.traverse import get_latest_rating_cache

import os

from ._template import (
    template_enchant, 
    template_equip, 
    template_talent, 
    template_other, 
    template_show
)

def _rating_icon_html(grade: str | None) -> str:
    if not grade:
        return ""
    icon = Path(
        build_path(ASSETS, ["image", "jx3", "rank", f"rank_{grade.lower()}.png"])
    ).as_uri()
    return (
        f'<img src="{icon}" '
        'style="position: absolute; top: 32px; left: -20px; '
        'width: 42px; height: 42px; object-fit: contain; z-index: 3;">'
    )

async def parse_equip(equip: Equip, last: bool = False, rating_grade: str | None = None) -> str:
    result = Template(
        (
            template_equip
            if last
            else template_equip + "<div class=\"divider\"></div>"
        )
    ).render(
        icon=await cache_image(equip.icon),
        name=equip.name,
        attr=equip.attribute,
        color=equip.color,
        quality=equip.quality,
        source=equip.source, # 不是推栏拿不到
        strength="⭐️" * equip.strength,
        effect=equip.effect,
        box=(
            Path(
                build_path(
                    ASSETS,
                    [
                        "image",
                        "jx3",
                        "attributes",
                        "not_max_strength.png"
                        if equip.strength < equip.max_strength
                        else "max_strength.png",
                    ],
                )
            ).as_uri()
        )
        if not (equip.color == "(255, 165, 0)")
        else Path(
            build_path(ASSETS, ["image", "jx3", "attributes", "flicker.png"])
        ),
        enchants=[
            Template(template_enchant).render(
                icon=icon,
                name=name
            )
            for icon, name
            in [
                (
                    Path(
                        ASSETS + "/image/jx3/attributes/permanent_enchant.png"
                    ).as_uri(),
                    equip.permanent_enchant
                ),
                (
                    Path(
                        ASSETS + "/image/jx3/attributes/common_enchant.png"
                    ).as_uri(),
                    (equip.common_enchant if equip.location_index not in [0, 1] else "")
                ),
                (
                    Path(
                        await cache_image(equip.color_stone_icon)
                    ).as_uri(),
                    equip.color_stone
                )
            ]
            if name
        ],
        fivestones={
            attr: Path(
                ASSETS + "/image/jx3/attributes/wuxingshi/" + str(level) + ".png"
            ).as_uri()
            for attr, level
            in equip.diamonds
        },
        peerless="<img src=\""
        + Path(
            build_path(ASSETS, ["image", "jx3", "attributes", "peerless.png"])
        ).as_uri()
        + "\" style=\"position: absolute;top: 0; left: -20px;\">"
        if equip.peerless
        else "",
        rating=_rating_icon_html(rating_grade)
    )
    return result

async def get_attr_v4(server: str, name: str, conditions: str = ""):
    role_info = await search_player(role_name=name, server_name=server)
    if not role_info.roleId:
        return PROMPT.PlayerNotExist
    # await JX3PlayerAttribute.from_tuilan(role_info.roleId, role_info.serverName, role_info.globalRoleId)
    await JX3PlayerAttribute.from_jx3api(role_info.serverName, role_info.roleName, True)
    instance = await JX3PlayerAttribute.from_database(int(role_info.globalRoleId), conditions, True)
    if instance is None:
        return PROMPT.EquipNotFound
    current_equip = instance[0]
    other_equips = instance[1:]
    kungfu = Kungfu.with_internel_id(current_equip.kungfu_id)
    show: str | None = None
    show_path = SHOW + f"/{name}·{server}.png"
    if os.path.exists(show_path):
        show = Template(template_show).render(
            show_path=show_path
        )
    basic_info = {}
    basic_info["门派"] = role_info.forceName
    basic_info["体型"] = role_info.bodyName
    basic_info["阵营"] = role_info.campName
    basic_info["心法"] = kungfu.name or "未知"
    basic_info["标识"] = role_info.roleId
    basic_info["全服"] = role_info.globalRoleId
    main_attr, detailed_attr = split_display_attributes(current_equip.attributes, kungfu.abbr)
    all_equip_records = []
    for each_other_equip in other_equips:
        other_kungfu = Kungfu.with_internel_id(each_other_equip.kungfu_id, True)
        prefix = {"D": "DPS", "T": "T", "N": "HPS"}[other_kungfu.abbr]
        if other_kungfu.kungfu_name in ["惊羽诀", "天罗诡道", "太虚剑意", "紫霞功", "幽罗引"]:
            prefix = {
                "惊羽诀": "JY",
                "天罗诡道": "TL",
                "太虚剑意": "JC",
                "紫霞功": "QC",
                "幽罗引": "WX"
            }[other_kungfu.kungfu_name]
        all_equip_records.append(
            Template(template_other).render(
                icon=other_kungfu.icon,
                kungfu=other_kungfu.kungfu_name,
                tag=each_other_equip.tag,
                score=each_other_equip.score,
                msg=prefix + each_other_equip.tag,
            )
        )
    rating_cache = get_latest_rating_cache(current_equip.equip_lines, current_equip.kungfu_id)
    rating_by_location = {}
    if rating_cache is not None:
        rating_by_location = {
            rating["location_code"]: rating["grade"]
            for rating in rating_cache.ratings
            if "location_code" in rating and "grade" in rating
        }
    all_equips = current_equip.equips
    equips = [
        await parse_equip(e, rating_grade=rating_by_location.get(e.location_index))
        for e in all_equips[:-1]
    ] + [
        await parse_equip(
            all_equips[-1],
            True,
            rating_grade=rating_by_location.get(all_equips[-1].location_index),
        )
    ]
    talents = [
        Template(template_talent).render(
            icon=await cache_image(talent.icon),
            name=talent.name
        )
        for talent
        in current_equip.talents
    ]
    image = await get_attr_v4_image(
        name=name,
        server=server,
        basic_info=basic_info,
        main_attr=main_attr,
        detailed_attr=detailed_attr,
        all_equips=all_equip_records,
        show=(show or ""),
        score=current_equip.score,
        kungfu_icon=kungfu.icon,
        equips=equips,
        talents=talents
    )
    return image

async def get_attr_v4_image(
    name: str,
    server: str,
    basic_info: dict[str, str],
    main_attr: dict[str, str],
    detailed_attr: dict[str, str],
    all_equips: list[str],
    show: str | None,
    score: int,
    kungfu_icon: str,
    equips: list[str],
    talents: list[str]
):
    font = ASSETS + "/font/PingFangSC-Semibold.otf"
    info_margin = "12px"
    if show is not None:
        info_margin = "8px"
    html = Template(
        read(TEMPLATES + "/jx3/attributes_v4.html")
    ).render(
        info_margin=info_margin,
        name=name,
        server=server,
        info=basic_info,
        basic_attr=main_attr,
        detailed_attr=detailed_attr,
        score=score,
        kungfu_icon=kungfu_icon,
        equips=equips,
        talents=talents,
        other_equips=all_equips,
        font=font,
        saohua=get_saohua(),
        show=show
    )
    return await generate(
        html,
        ".container",
        segment=True,
        wait_for_network=True,
        viewport={"height": 1080, "width": 1920},
    )
