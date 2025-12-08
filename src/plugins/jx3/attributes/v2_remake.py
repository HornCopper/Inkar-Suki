from pathlib import Path
from typing import Literal, overload
from PIL import Image, ImageDraw, ImageFont

from nonebot.adapters.onebot.v11 import MessageSegment as ms

from src.const.prompts import PROMPT
from src.const.jx3.kungfu import Kungfu
from src.const.jx3.school import School
from src.const.path import (
    ASSETS,
    CACHE,
    build_path
)
from src.utils.file import write
from src.utils.generate import get_uuid
from src.utils.database.player import search_player
from src.utils.network import Request, cache_image
from src.utils.database.attributes import Equip, JX3PlayerAttribute, Talent
from src.utils.database.constant import EquipLocations

import os

async def get_school_background(school: str) -> str:
    image_path = build_path(ASSETS, ["image", "jx3", "attributes", "school_bg", school + ".png"])
    if os.path.exists(image_path):
        return image_path
    else:
        image = (await Request(f"https://cdn.jx3box.com/static/pz/img/overview/horizontal/{school}.png").get()).content
        write(image_path, image, "wb")
        return image_path

@overload
async def get_attr_v2_remake(server: str, role_name: str, segment: Literal[True]) -> ms | str: ...

@overload
async def get_attr_v2_remake(server: str, role_name: str, segment: Literal[False]) -> bytes | str: ...

async def get_attr_v2_remake(server: str, role_name: str, segment: bool = True):
    role_info = await search_player(role_name=role_name, server_name=server)
    if not role_info.roleId:
        return PROMPT.PlayerNotExist
    # await JX3PlayerAttribute.from_tuilan(role_info.roleId, role_info.serverName, role_info.globalRoleId)
    await JX3PlayerAttribute.from_jx3api(role_info.serverName, role_info.roleName, True)
    instance = await JX3PlayerAttribute.from_database(int(role_info.globalRoleId), all=False)
    if instance is None:
        return PROMPT.EquipNotFound
    kungfu = Kungfu.with_internel_id(instance.kungfu_id)
    image = await get_attr_v2_remake_img(
        role_name,
        role_info.bodyName,
        role_info.roleId,
        kungfu=kungfu,
        school=School(kungfu.school),
        equips=instance.equips,
        talents=instance.talents,
        panel=instance.attributes,
        score=instance.score
    )
    if not segment:
        return image
    return ms.image(image)

async def get_attr_v2_remake_global(global_role_id: int):
    instance = await JX3PlayerAttribute.from_database(global_role_id, all=False)
    if instance is None:
        return PROMPT.EquipNotFound
    kungfu = Kungfu.with_internel_id(instance.kungfu_id)
    image = await get_attr_v2_remake_img(
        "未知角色",
        "未知体型",
        "未知UID",
        kungfu=kungfu,
        school=School(kungfu.school),
        equips=instance.equips,
        talents=instance.talents,
        panel=instance.attributes,
        score=instance.score
    )
    return ms.image(image)

async def get_attr_v2_remake_build(jcl_line: str):
    instance = await JX3PlayerAttribute.frmo_jcl_line(jcl_line)
    instance.save()
    kungfu = Kungfu.with_internel_id(instance.kungfu_id)
    image = await get_attr_v2_remake_img(
        instance.name,
        "未知体型",
        "未知UID",
        kungfu=kungfu,
        school=School(kungfu.school),
        equips=instance.equips,
        talents=instance.talents,
        panel=instance.attributes,
        score=instance.score
    )
    return ms.image(image)

async def get_attr_v2_remake_img(
    name: str = "",
    body: str = "",
    role_id: str = "",
    kungfu: Kungfu = Kungfu(),
    school: School = School(),
    equips: list[Equip] = [],
    talents: list[Talent] = [],
    panel: dict[str, str] = {},
    score: int = 0
):
    medium = build_path(ASSETS, ["font", "PingFangSC-Medium.otf"])
    semibold = build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"])
    background = Image.open(
        await get_school_background(school.name or "少林")
    ).convert("RGBA")
    draw = ImageDraw.Draw(background)
    flickering = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "flicker.png"])).resize((38, 38)) # 稀世神兵
    precious = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "peerless.png"])) # 稀世装备
    max_strength_approching = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "max_strength.png"]))
    max_strength_unapproching = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "not_max_strength.png"])).resize((38, 38))
    common_enchant_icon = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "common_enchant.png"])).resize((20, 20)) # 大附魔
    permanent_enchant_icon = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "permanent_enchant.png"])).resize((20, 20)) # 小附魔
    filled_star = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "star_fill.png"])).convert("RGBA")
    empty_star = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "star_empty.png"])).convert("RGBA")
    pve = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "pve.png"])).resize((8, 8)).convert("RGBA")
    pvx = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "pvx.png"])).resize((8, 8)).convert("RGBA")
    pvp = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "pvp.png"])).resize((8, 8)).convert("RGBA")

    # 心法图标
    background.alpha_composite(Image.open(str(kungfu.icon)).resize((50, 50)), (61, 62))


    # 个人基本信息
    draw.text((84, 132), str(score), fill=(0, 0, 0),
              font=ImageFont.truetype(semibold, size=16), anchor="mm")
    draw.text((370, 70), name, fill=(255, 255, 255),
              font=ImageFont.truetype(semibold, size=32), anchor="mm")
    draw.text((370, 120), body + "·" + str(role_id), fill=(255, 255, 255),
              font=ImageFont.truetype(semibold, size=20), anchor="mm")
    
    # 奇穴
    draw.text((320, 435), "奇穴", fill=(255, 255, 255),
            font=ImageFont.truetype(semibold, size=20), anchor="mm")


    if len(talents) == 12:
        init_icon = 164
        init_text = 198
        y_icon = 479
        y_text = 530
        limit = 0
        done_time = 0
        for talent in talents:
            image = Image.open(await cache_image(talent.icon)).resize((39, 39))
            background.alpha_composite(image, (init_icon, y_icon))

            # 绘制文字
            draw.text(
                (init_text-15, y_text),
                talent.name,
                fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=12),
                anchor="mm",
            )

            # 更新位置
            init_icon += 54
            init_text += 54
            limit += 1

            if limit == 6:
                limit = 0
                init_icon = 164
                init_text = 198
                y_icon += 78
                y_text += 78
                done_time += 1
                if done_time == 2:
                    break
    elif len(talents) == 10:
        init_icon = 183
        init_text = 198
        y_icon = 479
        y_text = 530
        limit = 0
        done_time = 0

        for talent in talents:
            image = Image.open(await cache_image(talent.icon)).resize((39, 39))
            background.alpha_composite(image, (init_icon, y_icon))

            # 绘制文字
            draw.text(
                (init_text, y_text),
                talent.name,
                fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=12),
                anchor="mm",
            )

            # 更新位置
            init_icon += 65
            init_text += 67
            limit += 1

            if limit == 5:
                limit = 0
                init_icon = 183
                init_text = 198
                y_icon += 78
                y_text += 78
                done_time += 1
                if done_time == 2:
                    break

    else:
        init_icon = 227
        init_text = 246
        y_icon = 479
        y_text = 530
        limit = 0
        done_time = 0
        for talent in talents:
            image = Image.open(await cache_image(talent.icon)).resize((39, 39))
            background.alpha_composite(image, (init_icon, y_icon))

            # 绘制文字
            draw.text(
                (init_text, y_text),
                talent.name,
                fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=12),
                anchor="mm",
            )

            # 更新位置
            init_icon += 48*3
            init_text += 48*3
            limit += 1

            if limit == 2:
                limit = 0
                init_icon = 227
                init_text = 246
                y_icon += 68
                y_text += 68
                done_time += 1
                if done_time == 2:
                    break

    for dy in range(4):
        for dx in range(4):
            if dy*4 + dx == 12:
                break
            draw.text((130 + dx*128, 199 + dy*77), panel[list(panel)[dy*4 + dx]], fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=21), anchor="mm")
            draw.text((130 + dx*128, 222 + dy*77), list(panel)[dy*4 + dx], fill=(255, 255, 255),
                font=ImageFont.truetype(medium, size=14), anchor="mm")
    x, y = (703, 47)
    for equip in equips:
        if equip.icon:
            background.alpha_composite(Image.open(await cache_image(equip.icon)).resize((38, 38)), (x, y))
        if equip.peerless:
            background.alpha_composite(precious, (x - 20, y))
        if equip.max_strength == equip.strength:
            background.alpha_composite(max_strength_approching, (x, y))
        else:
            background.alpha_composite(max_strength_unapproching, (x, y))
        draw.text((x + 6 + 38, y + 10), equip.name, fill=(255, 255, 255),
            font=ImageFont.truetype(semibold, size=14), anchor="lm")
        draw.text((x + 6 + 38, y + 28), (str(equip.quality) + " " + equip.attribute), fill=(255, 255, 255),
            font=ImageFont.truetype(medium, size=12), anchor="lm")
        text_box = draw.textbbox((x + 6 + 38, y + 10), equip.name, font=ImageFont.truetype(semibold, size=14))
        for dy in range(int(equip.max_strength)):
            if dy <= int(equip.strength) - 1:
                background.alpha_composite(filled_star, (text_box[2] + 1 + dy*8, text_box[3] - 20))
            else:
                background.alpha_composite(empty_star, (text_box[2] + 1 + dy*8, text_box[3] - 20))
        draw.text((x + 242, y + 10), EquipLocations[equip.location_index], fill=(255, 255, 255),
            font=ImageFont.truetype(medium, size=12), anchor="lm")
        for dy in range(len(equip._diamonds)):
            background.alpha_composite(
                Image.open(
                    build_path(
                        ASSETS,
                        ["image", "jx3", "attributes", "wuxingshi", str(equip._diamonds[dy]) + ".png"]
                    )
                ).resize((20, 20)),
                (x + 242 + dy*20, y + 21))
        if len(equip.diamonds) == 1:
            draw.text((x + 242 + 20, y + 31), equip.diamonds[0][0], fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=12), anchor="lm")
        if len(equip.diamonds) == 2:
            text = ""
            for f in equip.diamonds:
                text = text + "/" + str(f[0])
            draw.text((x + 242 + 40, y + 31), text[1:], fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=12), anchor="lm")
        if len(equip.diamonds) == 3:
            text = ""
            for f in equip.diamonds[1:]:
                text = text + "/" + str(f[0])
            draw.text((x + 242 + 60, y + 11), equip.diamonds[0][0], fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=12), anchor="lm")
            draw.text((x + 242 + 60, y + 31), text[1:], fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=12), anchor="lm")
        enchant_count = 0
        if equip.permanent_enchant:
            background.alpha_composite(permanent_enchant_icon, (x + 358, y - 3 + enchant_count * 24))
            draw.text((x + 383, y + 6 + enchant_count*24), equip.permanent_enchant, fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=12), anchor="lm")
            enchant_count += 1
        if equip.common_enchant:
            background.alpha_composite(common_enchant_icon, (x + 358, y - 3 + enchant_count * 24))
            draw.text((x + 383, y + 6 + enchant_count*24), equip.common_enchant, fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=12), anchor="lm")
            enchant_count += 1
        if equip.color_stone:
            background.alpha_composite(Image.open(await cache_image(equip.color_stone_icon)).resize((20, 20)), (x + 358, y - 3 + enchant_count * 24))
            draw.text((x + 383, y + 6 + enchant_count*24), equip.color_stone, fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=12), anchor="lm")
            enchant_count += 1
        if equip.max_strength == 8:
            background.alpha_composite(flickering, (x, y))
        # if equip.belong == "pve":
        #     background.alpha_composite(pve, (x + 5, y + 5))
        # if equip.belong == "pvp":
        #     background.alpha_composite(pvp, (x + 5, y + 5))   
        # if equip.belong == "pvx":
        #     background.alpha_composite(pvx, (x + 5, y + 5))
        y += 49
    final_path = build_path(CACHE, [get_uuid() + ".png"])
    background.save(final_path)
    return Request(Path(final_path).as_uri()).local_content
