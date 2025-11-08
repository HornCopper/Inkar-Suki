from pathlib import Path
from typing import Literal
from PIL import Image, ImageFont, ImageDraw
from pydantic import BaseModel

from src.const.path import ASSETS, CACHE, build_path
from src.const.jx3.kungfu import Kungfu
from src.const.jx3.school import School
from src.utils.network import Request, cache_image
from src.utils.generate import get_uuid
from src.plugins.jx3.attributes.v2_remake import (
    get_school_background
)

class BasicItem(BaseModel):
    icon: str = ""
    name: str = ""

class Panel(BaseModel):
    name: str = ""
    value: str = ""

class SingleAttr:
    def __init__(self, data: dict, speed_percent: bool = False):
        self.name: str = data["name"]
        self.percent: bool = data["percent"]
        self._value: float | int = data["value"]
        self.speed_percent = speed_percent

    @property
    def value(self):
        if self.percent:
            return str(self._value) + "%"
        if self.speed_percent and self.name == "加速":
            return "%.2f%%" % (self._value / 210078.0 * 100)
        return str(self._value)

class Enchant(BasicItem):
    type: Literal["cs", "pe", "ce"] = "pe"

class FiveStone(BaseModel):
    level: int = 0
    attr: str | None = ""

class Talent(BasicItem):
    ...

from ._template import attr_map, location_map, panel_attr_d, panel_attr_n, panel_attr_t

class Equip(BasicItem):
    attribute: list[str] = []
    belong: Literal["pve", "pvp", "pvx"] = "pvx"
    enchant: list[Enchant] = [] # 包含五彩石
    fivestone: list[int] = []
    location: str = ""
    peerless: bool = False # 精简/特效/神兵
    quality: int = 0
    strength: tuple[int, int] = (0, 0)

def percent(v: float):
    return str(round(v, 2)) + "%"

async def get_equips(force_id: str, condition: list) -> list | str:
    params = {
        "per": 10,
        "page": 1,
        "tags": "".join(condition),
        "client": "std",
        "global_level": 130,
        "mount": force_id,
        "star": 1
    }
    data = (await Request("https://cms.jx3box.com/api/cms/app/pz", params=params).get()).json()
    data = data["data"]["list"]
    if len(data) == 0:
        return "未找到配装，请修改查询条件后再试！"
    else:
        return data

async def get_attr_recommend_image(
    name: str = "",
    nickname: str = "",
    box_uid: str = "",
    kungfu: Kungfu = Kungfu(),
    school: School = School(),
    equips: list[Equip] = [],
    talents: list[Talent] = [],
    panel: list[Panel] = [],
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

    # 心法图标
    background.alpha_composite(Image.open(str(kungfu.icon)).resize((50, 50)), (61, 62))


    # 个人基本信息
    draw.text((84, 132), str(score), fill=(0, 0, 0),
              font=ImageFont.truetype(semibold, size=16), anchor="mm")
    draw.text((370, 70), name, fill=(255, 255, 255),
              font=ImageFont.truetype(semibold, size=32), anchor="mm")
    draw.text((370, 120), nickname + "·" + str(box_uid), fill=(255, 255, 255),
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
            draw.text((130 + dx*128, 199 + dy*77), panel[dy*4 + dx].value, fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=21), anchor="mm")
            draw.text((130 + dx*128, 222 + dy*77), panel[dy*4 + dx].name, fill=(255, 255, 255),
                font=ImageFont.truetype(medium, size=14), anchor="mm")
    x, y = (703, 47)
    for equip in equips:
        background.alpha_composite(Image.open(await cache_image(equip.icon)).resize((38, 38)), (x, y))
        if equip.peerless:
            background.alpha_composite(precious, (x - 20, y))
        if equip.strength[0] == equip.strength[1]:
            background.alpha_composite(max_strength_approching, (x, y))
        else:
            background.alpha_composite(max_strength_unapproching, (x, y))
        draw.text((x + 6 + 38, y + 10), (f"{equip.name}({equip.strength[0]}/{equip.strength[1]})"), fill=(255, 255, 255),
            font=ImageFont.truetype(semibold, size=14), anchor="lm")
        draw.text((x + 6 + 38, y + 28), " ".join([str(equip.quality)] + equip.attribute), fill=(255, 255, 255),
            font=ImageFont.truetype(medium, size=12), anchor="lm")
        draw.text((x + 242, y + 10), equip.location, fill=(255, 255, 255),
            font=ImageFont.truetype(medium, size=12), anchor="lm")
        for dy in range(len(equip.fivestone)):
            background.alpha_composite(
                Image.open(
                    build_path(
                        ASSETS,
                        ["image", "jx3", "attributes", "wuxingshi", str(equip.fivestone[dy]) + ".png"]
                    )
                ).resize((20, 20)),
                (x + 242 + dy*20, y + 21))
        for dy in range(len(equip.enchant)):
            background.alpha_composite(
                (
                    permanent_enchant_icon
                    if equip.enchant[dy].name == "pe"
                    else common_enchant_icon
                    if equip.enchant[dy].name == "ce"
                    else Image.open(await cache_image(equip.enchant[dy].icon)).resize((20, 20))
                ),
                (x + 351, y - 3 + dy * 24)
            )
            draw.text((x + 375, y + 6 + dy*24), equip.enchant[dy].name, fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=12), anchor="lm")
        if equip.strength[1] == 8:
            background.alpha_composite(flickering, (x, y))
        y += 49
    final_path = build_path(CACHE, [get_uuid() + ".png"])
    background.save(final_path)
    return Request(Path(final_path).as_uri()).local_content

async def get_equip_image(id: str):
    data = (await Request(f"https://cms.jx3box.com/api/cms/app/pz/{id}").get()).json()
    kungfu = Kungfu.with_internel_id(data["data"]["mount"])
    equip_place = [
        "HAT", 
        "JACKET",
        "BELT", 
        "WRIST",
        "BOTTOMS",
        "SHOES",
        "NECKLACE",
        "PENDANT", 
        "RING_1", 
        "RING_2", 
        "SECONDARY_WEAPON",
        "PRIMARY_WEAPON"
    ] if kungfu not in ["问水诀", "山居剑意"] else [
        "HAT", 
        "JACKET",
        "BELT", 
        "WRIST",
        "BOTTOMS",
        "SHOES",
        "NECKLACE",
        "PENDANT", 
        "RING_1", 
        "RING_2", 
        "SECONDARY_WEAPON",
        "PRIMARY_WEAPON",
        "TERTIARY_WEAPON"
    ]
    equips = data["data"]["overview"]["equips"]
    parsed_equips: list[Equip] = []
    for p in equip_place:
        equip_data = equips[p]
        enchants: list[Enchant] = []
        if "enhance" in equip_data:
            enchants.append(
                Enchant(
                    icon = ASSETS + "/image/jx3/attributes/permanent_enchant.png",
                    name = equip_data["enhance"],
                    type = "pe"
                )
            )
        if "enchant" in equip_data:
            enchants.append(
                Enchant(
                    icon = ASSETS + "/image/jx3/attributes/common_enchant.png",
                    name = equip_data["enchant"],
                    type = "ce"
                )
            )
        if "stone" in equip_data:
            enchants.append(
                Enchant(
                    icon = "https://icon.jx3box.com/icon/" + str(equip_data["stone_icon"]) + ".png",
                    name = equip_data["stone"],
                    type = "cs"
                )
            )
        parsed_equips.append(
            Equip(
                icon = "https://icon.jx3box.com/icon/" + str(equip_data["icon"]) + ".png",
                name = equip_data["name"],
                attribute = [attr_map[a] for a in equip_data["attrs"]],
                enchant = enchants,
                fivestone = equip_data["embedding"],
                location = location_map[p],
                peerless = equip_data["is_special"],
                quality = equip_data["level"],
                strength = (equip_data["strength"], equip_data["max_strength_level"])
            )
        )
    image = await get_attr_recommend_image(
        name=data["data"]["title"],
        nickname=data["data"]["pz_author_info"]["display_name"],
        box_uid=data["data"]["user_id"],
        kungfu=kungfu,
        school=School(kungfu.name),
        equips=parsed_equips,
        talents=[
            Talent(
                icon = "https://icon.jx3box.com/icon/" + str(t["icon"]) + ".png",
                name  = t["name"]
            )
            for t
            in data["data"]["talent_pzcode"] or []
        ],
        panel=[
            Panel(
                name = m["label"] if (kungfu.base is not None and m["label"] == "主属性") else "根骨" if (kungfu.abbr == "N" and m["label"] == "主属性") else m["label"],
                value = percent(data["data"]["overview"]["attrs"][m["key"]] * 100) if isinstance(data["data"]["overview"]["attrs"][m["key"]], float) else str(data["data"]["overview"]["attrs"][m["key"]])
            )
            for m
            in (panel_attr_d if kungfu.abbr == "D" else panel_attr_n if kungfu.abbr == "N" else panel_attr_t)
        ],
        score=data["data"]["overview"]["score"]
    )
    return image