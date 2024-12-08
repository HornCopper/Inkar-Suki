from pathlib import Path
from typing import Literal, overload
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel

from nonebot.adapters.onebot.v11 import MessageSegment as ms

from src.const.prompts import PROMPT
from src.const.jx3.kungfu import Kungfu
from src.const.jx3.school import School
from src.const.jx3.server import Server
from src.const.path import (
    ASSETS,
    CACHE,
    build_path
)
from src.utils.decorators import time_record
from src.utils.file import read, write
from src.utils.generate import get_uuid
from src.utils.exceptions import QixueDataUnavailable
from src.utils.database.player import search_player
from src.utils.network import Request

import os
import json

from .mobile_attr import mobile_attribute_calculator

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

class Equip(BasicItem):
    attribute: list[str] = []
    belong: Literal["pve", "pvp", "pvx"] = "pvx"
    enchant: list[Enchant] = [] # 包含五彩石
    fivestone: list[int] = []
    location: str = ""
    peerless: bool = False # 精简/特效/神兵
    quality: int = 0
    strength: tuple[int, int] = (0, 0)

class Talent(BasicItem):
    ...

class Qixue:
    qixue_data: dict = {}

    def __init__(self, qixue: dict, kungfu: str):
        self.data = qixue
        self.kungfu = kungfu

    @classmethod
    async def initialize_qixue_data(cls):
        """类方法，用于异步初始化 qixue_data"""
        if cls.qixue_data == {}:
            cls.qixue_data = await cls.get_qixue_data()

    @classmethod
    async def create(cls, qixue: dict, kungfu: str):
        """异步创建实例，并确保 qixue_data 被初始化"""
        await cls.initialize_qixue_data()
        return cls(qixue, kungfu)
    
    @staticmethod
    async def get_qixue_data() -> dict:
        qixue_data_path = build_path(ASSETS, ["source", "jx3", "qixue_latest.json"])
        if os.path.exists(qixue_data_path):
            return json.loads(read(qixue_data_path))
        data = (await Request("https://data.jx3box.com/talent/std/index.json").get()).json()
        for each_ver in data:
            if each_ver["name"].find("体服") == -1:
                qixue_data = (await Request("https://data.jx3box.com/talent/std/" + each_ver["version"] + ".json").get()).json()
                write(qixue_data_path, json.dumps(qixue_data, ensure_ascii=False))
                return qixue_data
        raise QixueDataUnavailable
    
    @property
    def name(self) -> str:
        return self.data["name"]
    
    @property
    def location(self) -> tuple[str, str, str] | None:
        for x in self.qixue_data[self.kungfu]:
            for y in self.qixue_data[self.kungfu][x]:
                if self.qixue_data[self.kungfu][x][y]["name"] == self.name:
                    return x, y, "https://icon.jx3box.com/icon/" + str(self.qixue_data[self.kungfu][x][y]["icon"]) + ".png"

async def get_school_background(school: str) -> str:
    image_path = build_path(ASSETS, ["image", "jx3", "attributes", "school_bg", school + ".png"])
    if os.path.exists(image_path):
        return image_path
    else:
        image = (await Request(f"https://cdn.jx3box.com/static/pz/img/overview/horizontal/{school}.png").get()).content
        write(image_path, image, "wb")
        return image_path
    
async def download_image(image_url: str) -> str:
    file_name = image_url.split("/")[-1].split("?")[0]
    if image_url.endswith("unknown.png"):
        return build_path(ASSETS, ["image", "jx3", "attributes", "unknown.png"])
    final_path = build_path(ASSETS, ["image", "jx3", "attributes", "equips"], end_with_slash=True) + file_name
    if os.path.exists(final_path):
        return final_path
    else:
        try:
            main = (await Request(image_url).get()).content
        except:  # noqa: E722
            return image_url
        write(final_path, main, "wb")
        return final_path
    
class EquipDataProcesser:
    locations = ["帽子", "上衣", "腰带", "护手", "下装", "鞋子", "项链", "腰坠", "戒指", "戒指", "远程武器", "近身武器"]
    special_weapons = ["雪凤冰王笛", "血影天宇舞姬", "炎枪重黎", "腾空", "画影", "金刚", "岚尘金蛇", "苌弘化碧", "蝎心忘情", "抱朴狩天", "八相连珠", "圆月双角", "九龙升景", "斩马刑天", "风雷瑶琴剑", "五相斩", "雪海散华", "麒王逐魂"]

    def __init__(self, data: dict, name: str = ""):
        self.data = data
        self._cached_equips = None
        self.name = name

    @property
    def kungfu(self) -> Kungfu:
        return Kungfu.with_internel_id(
            self.data["data"]["Kungfu"]["KungfuID"]
        )
    
    @property
    def score(self) -> int:
        return self.data["data"]["TotalEquipsScore"]
    
    def _parse_attributes(self, data: dict) -> str:
        msg = ""
        for i in data["ModifyType"]:
            content = i["Attrib"]["GeneratedMagic"].split("提高")
            if len(content) == 1:
                content = content[0].split("增加")
            attr = content[0]
            attr = attr.replace("外功防御", "外防")
            attr = attr.replace("内功防御", "内防")
            attr = attr.replace("会心效果", "会效")
            filter_string = ["全", "阴性", "阳性", "阴阳", "毒性", "攻击", "值", "成效", "内功", "外功", "体质", "根骨", "力道", "元气", "身法", "等级", "混元性", "招式产生威胁", "水下呼吸时间", "抗摔系数", "马术气力上限", "气力上限"]
            for y in filter_string:
                attr = attr.replace(y, "")
            if attr != "" and len(attr) <= 4:
                msg = msg + f" {attr}"
        msg = msg.replace(" 能 ", " 全能 ").replace(" 能", " 全能")
        return msg.strip()

    def _format_equip(self, equip_data: dict, location: str) -> Equip:
        if not equip_data:
            return Equip()
        attributes = self._parse_attributes(equip_data)
        belong: Literal["pve", "pvx", "pvp"] = equip_data["EquipType"]["Icon"][-7:-4]
        if belong not in ["pve", "pvx", "pvp"]:
            belong = "pve"
        enchant = []
        if "WPermanentEnchant" in equip_data:
            enchant.append(
                Enchant(
                    icon = build_path(ASSETS, ["image", "jx3", "attributes", "permanent_enchant.png"]),
                    name = equip_data["WPermanentEnchant"]["Name"],
                    type = "pe"
                )
            )
        if "WCommonEnchant" in equip_data:
            attrs_ = json.dumps(equip_data["ModifyType"], ensure_ascii=False)
            if attrs_.find("攻击") != -1:
                type_ = "伤"
            elif attrs_.find("治疗") != -1:
                type_ = "疗"
            else:
                type_ = "御"
            with open(
                build_path(
                    ASSETS,
                    [
                        "source",
                        "jx3",
                        "enchant_mapping.json"
                    ]
                ),
                encoding="utf8",
                mode="r"
            ) as f:
                enchant_data: dict = json.loads(f.read())
                for enchant_name in enchant_data:
                    if enchant_data[enchant_name]["min"] <= int(equip_data["Quality"]) <= enchant_data[enchant_name]["max"]:
                        enchant.append(
                            Enchant(
                                icon = build_path(ASSETS, ["image", "jx3", "attributes", "common_enchant.png"]),
                                name = f"{enchant_name}·{type_}·" + {"帽子": "帽","上衣": "衣","腰带": "腰","护臂": "腕","鞋": "鞋"}[equip_data["Icon"]["SubKind"]],
                                type = "ce"
                            )
                        )
        if "effectColorStone" in equip_data:
            enchant.append(
                Enchant(
                    icon = equip_data["effectColorStone"]["Icon"]["FileName"],
                    name = equip_data["effectColorStone"]["Name"],
                    type = "cs"
                )
            )
        if location != "戒指" and "FiveStone" not in equip_data:
            equip_data["FiveStone"] = [
                {
                    "Level": "0"
                }
                for _
                in {
                    "帽子": 2,
                    "上衣": 2,
                    "腰带": 2,
                    "护手": 2,
                    "下装": 2,
                    "鞋子": 2,
                    "项链": 1,
                    "腰坠": 1,
                    "远程武器": 1,
                    "近身武器": 3
                }[location]
            ]
        fivestone = [
            int(fivestone["Level"])
            for fivestone
            in equip_data["FiveStone"]
        ] if location != "戒指" else []
        icon = equip_data["Icon"]["FileName"]
        name = equip_data["Name"]
        peerless = (equip_data["BelongForce"] in ["内功门派", "外功门派"]) \
        or (equip_data["MaxStrengthLevel"] == "8") \
        or (equip_data["Name"] in self.special_weapons) \
        or (any(d.get('Desc') == 'atSkillEventHandler' for d in equip_data["ModifyType"])) \
        or (equip_data.get("Desc", "").startswith("使用："))
        quality = equip_data["Quality"]
        strength = (int(equip_data["StrengthLevel"]), int(equip_data["MaxStrengthLevel"]))
        return Equip(
            attribute=attributes.split(" "),
            belong=belong,
            enchant=enchant,
            fivestone=fivestone,
            icon=icon,
            location=location,
            name=name,
            peerless=peerless,
            quality=quality,
            strength=strength
        )
    
    @property
    def equips(self) -> list[Equip]:
        if self.kungfu.school == "藏剑":
            self.locations.append("近身武器")
        if self._cached_equips is not None:
            return [
                self._format_equip(equip, location)
                for equip, location in zip(self._cached_equips, self.locations)
            ]

        equip_map = {
            "帽子": 0, "上衣": 1, "腰带": 2, "护臂": 3, "裤子": 4, 
            "鞋": 5, "项链": 6, "腰坠": 7, "戒指": [8, 9], 
            "投掷囊": 10, "武器": 11, "重剑": 12
        }
        equips_list = [{}] * 13
        rings = iter(equip_map["戒指"])
        try:
            data = self.data["data"]["Equips"]
        except TypeError:
            raise ValueError("玩家似乎在提交角色给音卡后删除了账号！")
        
        for equip in data:
            subkind = equip["Icon"]["SubKind"]
            kind = equip["Icon"]["Kind"]
            if subkind == "戒指":
                equips_list[next(rings)] = equip
            elif subkind in equip_map:
                equips_list[equip_map[subkind]] = equip
            elif kind == "武器" or (kind == "任务特殊" and subkind == "活动相关"):
                equips_list[equip_map["武器"]] = equip
        
        self._cached_equips = equips_list if self.kungfu.school == "藏剑" else equips_list[:12]
        return [
            self._format_equip(equip, location)
            for equip, location in zip(self._cached_equips, self.locations)
        ]

    async def qixue(self) -> list[Talent]:
        qixue_list = self.data["data"]["Person"]["qixueList"]
        unknown_img = build_path(ASSETS, ["image", "jx3", "attributes", "unknown.png"])
        name = ["未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知"]
        icon = [unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img]
        kungfu = self.kungfu.name
        if qixue_list == [] or kungfu is None or kungfu.endswith("·悟"):
            return [
                Talent(icon=each_icon, name=each_name)
                for each_name, each_icon
                in zip(name, icon)
            ]
        for single_qixue in qixue_list:
            location = (await Qixue.create(single_qixue, kungfu)).location
            if location is None:
                continue
            x, y, _icon = location
            name[int(x)-1] = single_qixue["name"]
            icon[int(x)-1] = _icon
        return [
            Talent(icon=each_icon, name=each_name)
            for each_name, each_icon
            in zip(name, icon)
        ]

    @property
    def panel_types(self) -> list[str]:
        if self.kungfu.base in ["根骨", "元气", "力道", "身法"]:
            return ["面板攻击", "基础攻击", "会心", "会心效果", "加速", self.kungfu.base, "破防", "无双", "破招", "最大气血值", "御劲", "化劲"]   
        elif self.kungfu.base == "治疗":
            return ["面板治疗量", "基础治疗量", "会心", "会心效果", "加速", "根骨", "外功防御", "内功防御", "破招", "最大气血值", "御劲", "化劲"]
        elif self.kungfu.base == "防御":
            return ["外功防御", "内功防御", "最大气血值", "破招", "御劲", "闪避", "招架", "拆招", "体质", "加速率", "无双", "加速"]
        else:
            return ["未知属性"] * 12

    def _panel_type(self, panel_attr_name: str) -> SingleAttr:
        """
        将面板展示的属性转换为实际需要的属性，并传出已有数据的对应属性字典。
        """
        panel_attr_map = {
            "面板攻击": "攻击力",
            "基础攻击": "基础攻击力",
            "最大气血值": "气血",
            "面板治疗量": "治疗量",
            "基础治疗量": "治疗量",
            "外防": "外功防御",
            "内防": "内功防御"
        }
        if panel_attr_name in panel_attr_map:
            panel_attr_name = panel_attr_map[panel_attr_name]
        speed_percent = False
        if panel_attr_name == "加速率":
            speed_percent = True
        for attr in self.data["data"]["PersonalPanel"]:
            if attr["name"] == panel_attr_name:
                return SingleAttr(attr, speed_percent)
        for attr in self.data["data"]["PersonalPanel"]:
            if attr["name"] == "加速":
                return SingleAttr(attr, speed_percent)
        raise ValueError(f"Unexpected attribute `{panel_attr_name}`!")

    @property
    def panel_values(self) -> list[str]:
        attr_types = self.panel_types
        result = []
        if self.data["data"]["PersonalPanel"] is None:
            name = self.kungfu.name
            if name is None:
                return ["N/A"] * 12
            if name.endswith("·悟"):
                name = name[:-2]
            result = mobile_attribute_calculator(self.data["data"]["Equips"], name, attr_types)
            return result
        if self.kungfu.base is not None and self.data["data"]["PersonalPanel"] is not None:
            for attr_type in attr_types:
                result.append(self._panel_type(attr_type).value)
            return result
        else:
            return ["N/A"] * 12
        
    @property
    def panel(self) -> list[Panel]:
        return [
            Panel(
                name = name,
                value = value
            )
            for name, value
            in zip(
                self.panel_types,
                self.panel_values
            )
        ]
    
@overload
async def get_attr_v2_remake(server: str, role_name: str, segment: Literal[True]) -> ms | str: ...

@overload
async def get_attr_v2_remake(server: str, role_name: str, segment: Literal[False]) -> bytes | str: ...

async def get_attr_v2_remake(server: str, role_name: str, segment: bool = True):
    player = (await search_player(role_name=role_name, server_name=server)).format_jx3api()
    if player["code"] != 200:
        return PROMPT.PlayerNotExist
    params = {
        "zone": Server(server).zone,
        "server": server,
        "game_role_id": player["data"]["roleId"]
    }
    data = (await Request("https://m.pvp.xoyo.com/mine/equip/get-role-equip", params=params).post(tuilan=True)).json()
    data_object = EquipDataProcesser(data, role_name)
    try:
        data_object.equips
    except TypeError:
        return "玩家似乎在提交角色之后转服或删除！\n或是装备并未穿戴完整，例如浪客行装备，请检查后重试！"
    image = await get_attr_v2_remake_img(
        role_name,
        player["data"]["bodyName"],
        player["data"]["roleId"],
        kungfu=data_object.kungfu,
        school=School(data_object.kungfu.school),
        equips=data_object.equips,
        talents=(await data_object.qixue()),
        panel=data_object.panel,
        score=data_object.score
    )
    if not segment:
        return image
    return ms.image(image)

async def get_attr_v2_remake_img(
    name: str = "",
    body: str = "",
    role_id: str = "",
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
    
    init_icon = 179
    init_text = 199
    y_icon = 479
    y_text = 530
    limit = 0
    done_time = 0

    for talent in talents:
        image = Image.open(await download_image(talent.icon)).resize((39, 39))
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
        init_icon += 48
        init_text += 48
        limit += 1

        if limit == 6:
            limit = 0
            init_icon = 179
            init_text = 199
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
        background.alpha_composite(Image.open(await download_image(equip.icon)).resize((38, 38)), (x, y))
        if equip.peerless:
            background.alpha_composite(precious, (x - 20, y))
        if equip.strength[0] == equip.strength[1]:
            background.alpha_composite(max_strength_approching, (x, y))
        else:
            background.alpha_composite(max_strength_unapproching, (x, y))
        draw.text((x + 6 + 38, y + 10), equip.name, fill=(255, 255, 255),
            font=ImageFont.truetype(semibold, size=14), anchor="lm")
        draw.text((x + 6 + 38, y + 28), " ".join([str(equip.quality)] + equip.attribute), fill=(255, 255, 255),
            font=ImageFont.truetype(medium, size=12), anchor="lm")
        text_box = draw.textbbox((x + 6 + 38, y + 10), equip.name, font=ImageFont.truetype(semibold, size=14))
        for dy in range(int(equip.strength[1])):
            if dy <= int(equip.strength[0]) - 1:
                background.alpha_composite(filled_star, (text_box[2] + 1 + dy*8, text_box[3] - 20))
            else:
                background.alpha_composite(empty_star, (text_box[2] + 1 + dy*8, text_box[3] - 20))
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
                    else Image.open(await download_image(equip.enchant[dy].icon)).resize((20, 20))
                ),
                (x + 351, y - 3 + dy * 24)
            )
            draw.text((x + 375, y + 6 + dy*24), equip.enchant[dy].name, fill=(255, 255, 255),
                font=ImageFont.truetype(semibold, size=12), anchor="lm")
        if equip.strength[1] == 8:
            background.alpha_composite(flickering, (x, y))
        if equip.belong == "pve":
            background.alpha_composite(pve, (x + 5, y + 5))
        if equip.belong == "pvp":
            background.alpha_composite(pvp, (x + 5, y + 5))   
        if equip.belong == "pvx":
            background.alpha_composite(pvx, (x + 5, y + 5))
        y += 49
    final_path = build_path(CACHE, [get_uuid() + ".png"])
    background.save(final_path)
    return Request(Path(final_path).as_uri()).local_content