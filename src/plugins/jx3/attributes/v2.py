from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Literal
from nonebot.adapters.onebot.v11 import MessageSegment as ms

from src.config import Config
from src.const.prompts import PROMPT
from src.const.jx3.kungfu import Kungfu
from src.const.path import (
    ASSETS,
    CACHE,
    build_path
)
from src.utils.decorators import time_record
from src.utils.file import write
from src.utils.generate import get_uuid
from src.utils.database.player import search_player
from src.utils.database.attributes import AttributesRequest
from src.utils.network import Request
from src.plugins.jx3.attributes.v2_remake import Qixue

import os
import json

bot_name = Config.bot_basic.bot_name_argument
token = Config.jx3.api.token
ticket = Config.jx3.api.ticket
device_id = ticket.split("::")[-1]

async def get_personal_data(server, id) -> Literal[False] | tuple[str, str, str]:
    role_info = await search_player(role_name=id, server_name=server)
    if role_info.roleId == "":
        return False
    else:
        return role_info.roleId, role_info.bodyName, role_info.forceName
        # UID 体型 门派

class Enchant:
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

    def __init__(self, quality: int):
        self.quality = int(quality)

    @property
    def name(self) -> str | None:
        for enchant_name in self.enchant_data:
            if self.enchant_data[enchant_name]["min"] <= self.quality <= self.enchant_data[enchant_name]["max"]:
                return enchant_name

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

class JX3AttributeV2:
    def __init__(self, data: dict):
        self.data = data
        self._cached_equips = None 

    @property
    def _meta_school(self) -> Kungfu:
        kungfu_instance = Kungfu.with_internel_id(self.data["data"]["Kungfu"]["KungfuID"])
        return kungfu_instance
    
    @property
    def school(self) -> str | None:
        return self._meta_school.school
    
    @property
    def kungfu(self) -> str | None:
        name = self._meta_school.name
        if name is None:
            return None
        name = name.replace("决", "诀")
        if name == "山居剑意":
            name = "问水诀"
        return name
    
    @staticmethod
    def get_fivestone_icon(level: int) -> str:
        return build_path(
            ASSETS,
            [
                "wuxingshi",
                str(level) + ".png"
            ]
        )

    @staticmethod
    async def background(school: str):
        """
        获取门派背景图。

        Args:
            school (str): 可能存在无界玩家的`KungfuId`无法识别，建议自行传入门派。
        """
        if school in ["万灵山庄", "衍天宗", "凌雪阁"]:
            school = school[0:2]
        if school == "北天药宗":
            school = school[-2:]
        final_path = build_path(ASSETS, ["image", "jx3", "attributes", "school_bg", school + ".png"])
        if os.path.exists(final_path):
            return final_path
        else:
            data = (await Request(f"https://cdn.jx3box.com/static/pz/img/overview/horizontal/{school}.png").get()).content
            write(final_path, data, "wb")
            return final_path
        
    @property
    def kungfu_icon(self):
        """
        获取心法图标。

        无界可能无法获得心法图标，使用通用图标。
        """
        if self.kungfu is None:
            return build_path(
                ASSETS,
                [
                    "image",
                    "jx3",
                    "kungfu",
                    "通用.png"
                ]
            )
        return build_path(
            ASSETS,
            [
                "image",
                "jx3",
                "kungfu",
                self.kungfu + ".png"
            ]
        )

    @property
    def attr_types(self) -> list[str]:
        if self._meta_school.base in ["根骨", "元气", "力道", "身法"]:
            return ["面板攻击", "基础攻击", "会心", "会心效果", "加速", self._meta_school.base, "破防", "无双", "破招", "最大气血值", "御劲", "化劲"]   
        elif self._meta_school.base == "治疗":
            return ["面板治疗量", "基础治疗量", "会心", "会心效果", "加速", "根骨", "外防", "内防", "破招", "最大气血值", "御劲", "化劲"]
        elif self._meta_school.base == "防御":
            return ["外防", "内防", "最大气血值", "破招", "御劲", "闪避", "招架", "拆招", "体质", "加速率", "无双", "加速"]
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
    def attr_values(self) -> list[str]:
        attr_types = self.attr_types
        result = []
        if self._meta_school.base is not None and self.data["data"]["PersonalPanel"] is not None if "PersonalPanel" in self.data["data"] else True:
            for attr_type in attr_types:
                result.append(self._panel_type(attr_type).value)
            return result
        else:
            return ["N/A"] * 12
    
    @property
    def equips(self) -> list[dict] | Literal[False]:
        if self._cached_equips is not None:
            return self._cached_equips
        
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

        if len(data) != (12 if self.kungfu != "问水诀" else 13):
            return False
        
        for equip in data:
            subkind = equip["Icon"]["SubKind"]
            kind = equip["Icon"]["Kind"]
            if subkind == "戒指":
                equips_list[next(rings)] = equip
            elif subkind in equip_map:
                equips_list[equip_map[subkind]] = equip
            elif kind == "武器" or (kind == "任务特殊" and subkind == "活动相关"):
                equips_list[equip_map["武器"]] = equip
        
        self._cached_equips = equips_list if self.kungfu in ["问水诀", "山居剑意"] else equips_list[:12]
        return self._cached_equips

    @property
    def five_stones(self) -> list[str]:
        results = []
        equips = self.equips
        if not equips:
            return [build_path(ASSETS, ["image", "jx3", "attributes", "wuxingshi", "0.png"])] * (18 if self.school != "藏剑" else 21)
        for equip in equips:
            if equip == {}:
                return [build_path(ASSETS, ["image", "jx3", "attributes", "wuxingshi", "0.png"])] * (18 if self.school != "藏剑" else 21)
            if isinstance(equip, dict) and equip["Icon"]["SubKind"] != "戒指":
                five_stones_list = equip.get("FiveStone", [])
                results.extend([build_path(ASSETS, ["image", "jx3", "attributes", "wuxingshi", str(b["Level"]) + ".png"]) for b in five_stones_list])
        return results
    
    @property
    def color_stone(self) -> Literal[False] | list[tuple[str, str]]:
        equips = self.equips
        if not equips:
            return False
        color_stones: list[tuple[str, str]] = []
        if self.kungfu == "问水诀":
            equips = equips[-2:]
        else:
            equips = equips[-1:]
        for each_equip in equips:
            if "effectColorStone" in each_equip:
                colorful_stone_name = each_equip["effectColorStone"]["Name"]
                colorful_stone_image = each_equip["effectColorStone"]["Icon"]["FileName"]
                color_stones.append((colorful_stone_name, colorful_stone_image))
            color_stones.append(("", ""))
        return color_stones
    
    @property
    def permanent_enchant(self) -> Literal[False] | list[str]:
        equips = self.equips
        result = []
        if not equips:
            return False
        for each_equip in equips:
            if "WPermanentEnchant" in each_equip:
                result.append(each_equip["WPermanentEnchant"]["Name"])
                continue
            result.append("")
        return result
    
    @property
    def common_enchant(self) -> Literal[False] | list[str]:
        equips = self.equips
        result = []
        if not equips:
            return False
        for location in ["帽子", "上衣", "腰带", "护臂", "鞋"]:
            for equip in equips:
                if equip == {}:
                    continue
                if equip["Icon"]["SubKind"] == location:
                    if "WCommonEnchant" in equip:
                        attrs_ = json.dumps(equip["ModifyType"], ensure_ascii=False)
                        if attrs_.find("攻击") != -1:
                            type_ = "伤"
                        elif attrs_.find("治疗") != -1:
                            type_ = "疗"
                        else:
                            type_ = "御"
                        enchant_name = Enchant(int(equip["Quality"])).name
                        if enchant_name is not None:
                            result.append(enchant_name + "·" + type_ + "·" + {"帽子": "帽","上衣": "衣","腰带": "腰","护臂": "腕","鞋": "鞋"}[location])
                            continue
                    result.append("")
        return result
    
    @property
    def equips_and_icons(self) -> Literal[False] | tuple[list[str], list[str]]:
        equips = self.equips
        if not equips:
            return False
        name = []
        icon = []
        for each in equips:
            if each == {}:
                name.append(
                    "未知（0/6）"
                )
                icon.append(
                    "unknown.png"
                )
                continue
            name.append(each["Name"] + "(" + each["StrengthLevel"] + "/" + each["MaxStrengthLevel"] + ")")
            icon.append(each["Icon"]["FileName"])
        return name, icon
    
    @property
    def strength(self) -> Literal[False] | tuple[list[str], list[str]]:
        equips = self.equips
        if not equips:
            return False
        max = []
        current = []
        for each in equips:
            if each == {}:
                max.append("6")
                current.append("0")
                continue
            max.append(each["MaxStrengthLevel"])
            current.append(each["StrengthLevel"])
        return max, current
    
    def _parse_attr(self, data: dict) -> str:
        msg = ""
        for i in data["ModifyType"]:
            content = i["Attrib"]["GeneratedMagic"].split("提高")
            if len(content) == 1:
                content = content[0].split("增加")
            attr = content[0]
            attr = attr.replace("外功防御", "外防")
            attr = attr.replace("内功防御", "内防")
            attr = attr.replace("会心效果", "会效")
            filter_string = ["全", "阴性", "阳性", "阴阳", "毒性", "攻击", "值", "成效", "内功", "外功", "体质", "根骨", "力道", "元气", "身法", "等级", "混元性", "招式产生威胁", "水下呼吸时间", "抗摔系数", "马术气力上限"]
            for y in filter_string:
                attr = attr.replace(y, "")
            if attr != "" and len(attr) <= 4:
                msg = msg + f" {attr}"
        msg = msg.replace(" 能 ", " 全能 ").replace(" 能", " 全能")
        return msg

    @property
    def qualities(self) -> Literal[False] | list[str]:
        equips = self.equips
        if not equips:
            return False
        quality = []
        for each in equips:
            if each == {}:
                quality.append("可能是推栏未识别？")
                continue
            quality.append(
                str(each["Quality"]) + " " + self._parse_attr(each)
            )
        return quality
    
    @property
    def precious(self) -> list[bool] | Literal[False]:
        equips = self.equips
        result = []
        if not equips:
            return False
        for each in equips:
            try:
                source = each["equipBelongs"][0]["source"]
            except (TypeError, IndexError, ValueError):
                source = ""
            if (each["BelongForce"] in ["内功门派", "外功门派"]) \
                or (each["MaxStrengthLevel"] == "8") \
                or special_weapon(each["Name"]) \
                or (any(d.get('Desc') == 'atSkillEventHandler' for d in each["ModifyType"])) \
                or (each.get("Desc", "").startswith("使用：")) \
                or (source.startswith("商店：叶鸦")):
                result.append(True)
            else:
                result.append(False)
        return result

    async def qixue(self) -> tuple[list[str], list[str]]:
        qixue_list = self.data["data"]["Person"]["qixueList"]
        unknown_img = build_path(ASSETS, ["image", "jx3", "attributes", "unknown.png"])
        name = ["未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知"]
        icon = [unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img]
        kungfu = self.kungfu
        if qixue_list == [] or kungfu is None:
            return name, icon
        if qixue_list == [] and kungfu.endswith("·悟"):
            return name, icon
        for single_qixue in qixue_list:
            location = (await Qixue.create(single_qixue, kungfu)).location
            if location is None:
                continue
            x, y, _icon = location
            name[int(x)-1] = single_qixue["name"]
            icon[int(x)-1] = _icon
        return name, icon
            
    @property
    def score(self) -> int:
        return self.data["data"]["TotalEquipsScore"]
        
@time_record
async def get_attr_v2(server: str, role_name: str):
    personal_data = await get_personal_data(server, role_name)
    if not personal_data:
        return "唔……未找到该玩家，请提交角色！\n提交角色 服务器 UID"
    uid, body, school = personal_data
    instance = await AttributesRequest.with_name(server, role_name)
    if not instance:
        return PROMPT.PlayerNotExist
    equip_data = instance.get_equip()
    if isinstance(equip_data, bool):
        return PROMPT.PlayerNotExist if equip_data else PROMPT.EquipNotFound
    attrsObject = JX3AttributeV2(equip_data)
    if not attrsObject.equips:
        return "唔……请把装备穿戴完整再来查询！\n有可能是推栏未识别部分装备，等待推栏更新即可！"
    max, current = attrsObject.strength or ([], [])
    equips, icons = attrsObject.equips_and_icons or ([], [])
    qixue_n, qixue_i = await attrsObject.qixue()
    color_stones = attrsObject.color_stone or [("", "")]
    precious_list = attrsObject.precious
    if school == "藏剑":
        c1n, c1i = color_stones[0]
        try:
            c2n, c2i = color_stones[1]
        except IndexError:
            c2n, c2i = "", ""
    else:
        c1n, c1i = color_stones[0]
        c2n, c2i = "", ""
    image = await get_attributes_image_v2(
        kungfu = Kungfu(attrsObject.kungfu),
        school_background = await attrsObject.background(school),
        max_strength = max,
        strength = current,
        equip_list = equips,
        equip_icon = icons,
        equip_quailty = attrsObject.qualities or [],
        basic_info = [str(attrsObject.score), role_name, school + "·" + body, uid],
        qixue_name = qixue_n,
        qixue_icon = qixue_i,
        common_enchant = attrsObject.common_enchant or [],
        permanent_enchant = attrsObject.permanent_enchant or [],
        five_stone = attrsObject.five_stones or [],
        color_stone_icon = c1i,
        color_stone_name = c1n,
        attribute_values = attrsObject.attr_values,
        color_stone_icon_2 = c2i,
        color_stone_name_2 = c2n,
        attr_types = attrsObject.attr_types,
        precious_list = precious_list or []
    )
    return ms.image(Request(image).local_content)


async def local_save(image_url: str) -> str:
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


def special_weapon(name: str) -> bool:
    special_weapons = ["雪凤冰王笛", "血影天宇舞姬", "炎枪重黎", "腾空", "画影", "金刚", "岚尘金蛇", "苌弘化碧", "蝎心忘情", "抱朴狩天", "八相连珠", "圆月双角", "九龙升景", "斩马刑天", "风雷瑶琴剑", "五相斩", "雪海散华", "麒王逐魂"]
    for i in special_weapons:
        if name.split("(")[0] in special_weapons:
            return True
    return False


async def get_attributes_image_v2(
    kungfu: Kungfu,
    school_background: str,
    max_strength: list,
    strength: list, 
    equip_list: list,
    equip_icon: list, 
    equip_quailty: list, 
    basic_info: list,
    qixue_name: list, 
    qixue_icon: list, 
    common_enchant: list, 
    permanent_enchant: list, 
    five_stone: list, 
    color_stone_icon: str,
    color_stone_name: str, 
    attribute_values: list, 
    color_stone_name_2: str, 
    color_stone_icon_2: str,
    attr_types: list[str],
    precious_list: list[bool]
):
    syst_bold = build_path(ASSETS, ["font", "syst-bold.ttf"])
    syst_mid = build_path(ASSETS, ["font", "syst-mid.ttf"])
    msyh = build_path(ASSETS, ["font", "msyh.ttf"])
    calibri = build_path(ASSETS, ["font", "calibri.ttf"])
    background = Image.open(school_background).convert("RGBA")
    draw = ImageDraw.Draw(background)
    flickering = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "flicker.png"])).resize((38, 38))
    precious = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "peerless.png"]))
    max_strength_approching = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "max_strength.png"]))
    max_strength_unapproching = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "not_max_strength.png"])).resize((38, 38))
    common_enchant_icon = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "common_enchant.png"])).resize((20, 20))
    permanent_enchant_icon = Image.open(build_path(ASSETS, ["image", "jx3", "attributes", "permanent_enchant.png"])).resize((20, 20))

    # 心法图标
    background.alpha_composite(Image.open(str(kungfu.icon)).resize((50, 50)), (61, 62))

    # 武器图标
    if kungfu.name not in ["问水诀", "山居剑意"]:
        if equip_icon[11] != "":
            background.alpha_composite(Image.open(await local_save(equip_icon[11])).resize((38, 38)), (708, 587))
            if max_strength[11] in ["3", "4", "8"] or special_weapon(equip_list[11]) or precious_list[11]:
                background.alpha_composite(precious, (688, 586))
                if max_strength[11] == "8":
                    background.alpha_composite(flickering, (707, 586))
                else:
                    if max_strength[11] == strength[11]:
                        background.alpha_composite(max_strength_approching, (708, 587))
            else:
                if max_strength[11] == strength[11]:
                    background.alpha_composite(max_strength_approching, (708, 587))
                else:
                    background.alpha_composite(max_strength_unapproching, (708, 587))
    else:
        if equip_icon[11] != "":
            background.alpha_composite(Image.open(await local_save(equip_icon[11])).resize((38, 38)), (708, 587))
            if max_strength[11] in ["3", "4", "8"] or special_weapon(equip_list[11]) or precious_list[11]:
                background.alpha_composite(precious, (688, 586))
                if max_strength[11] == "8":
                    background.alpha_composite(flickering, (708, 587))
                else:
                    if max_strength[11] == strength[11]:
                        background.alpha_composite(max_strength_approching, (708, 587))
            else:
                if max_strength[11] == strength[11]:
                    background.alpha_composite(max_strength_approching, (708, 587))
                else:
                    background.alpha_composite(max_strength_unapproching, (708, 587))
        if equip_icon[12] != "":
            if special_weapon(equip_list[12]) or precious_list[12]:
                background.alpha_composite(precious, (688, 635))
            background.alpha_composite(Image.open(await local_save(equip_icon[12])).resize((38, 38)), (708, 636))
            if max_strength[12] in ["3", "4", "8"]:
                background.alpha_composite(precious, (688, 635))
                if max_strength[12] == "8":
                    background.alpha_composite(flickering, (708, 636))
                else:
                    if max_strength[12] == strength[12]:
                        background.alpha_composite(max_strength_approching, (708, 636))
            else:
                if max_strength[12] == strength[12]:
                    background.alpha_composite(max_strength_approching, (708, 636))
                else:
                    background.alpha_composite(max_strength_unapproching, (708, 636))

    # 装备图标
    init = 48
    limit = 0
    for i in equip_icon:
        if i != "":
            background.alpha_composite(Image.open(await local_save(i)).resize((38, 38)), (708, init))
        init = init + 49
        limit = limit + 1
        if limit == 11:
            break

    # 装备精炼
    init = 47
    range_time = 11
    if kungfu.name in ["问水诀", "山居剑意"]:
        range_time = range_time + 1
    for i in range(range_time):
        if special_weapon(equip_list[i]) or precious_list[i]:
            background.alpha_composite(precious, (687, init - 1))
        if max_strength[i] in ["3", "4", "8"]:
            background.alpha_composite(precious, (687, init - 1))
        if strength[i] == max_strength[i]:
            background.alpha_composite(max_strength_approching, (707, init))
        else:
            if equip_list[i] != "":
                background.alpha_composite(max_strength_unapproching, (707, init))
        if max_strength[i] == "8":
            background.alpha_composite(flickering, (709, init + 2))
        init = init + 49

    # 装备名称
    init = 50
    for i in equip_list:
        if i != "":
            draw.text((752, init), i, fill=(255, 255, 255),
                      font=ImageFont.truetype(syst_bold, size=14), anchor="lt")
        init = init + 49

    # 装备品级 + 属性
    init = 71
    for i in equip_quailty:
        if i != "":
            draw.text((752, init), i, fill=(255, 255, 255),
                      font=ImageFont.truetype(syst_bold, size=14), anchor="lt")
        init = init + 49

    # 个人基本信息
    draw.text((85, 127), str(basic_info[0]), fill=(0, 0, 0),
              font=ImageFont.truetype(calibri, size=18), anchor="mt")
    draw.text((370, 70), basic_info[1], fill=(255, 255, 255),
              font=ImageFont.truetype(msyh, size=32), anchor="mm")
    draw.text((370, 120), basic_info[2], fill=(255, 255, 255),
              font=ImageFont.truetype(msyh, size=20), anchor="mm")
    draw.text((450, 120), basic_info[3], fill=(127, 127, 127),
              font=ImageFont.truetype(calibri, size=18), anchor="mm")

    # 面板内容
    positions = [(127, 226), (258, 226), (385, 226), (514, 226), (127, 303), (258, 303),
                 (385, 303), (514, 303), (127, 380), (258, 380), (385, 380), (514, 380)]
    range_time = 12
    for i in range(range_time):
        draw.text(positions[i], attr_types[i], fill=(255, 255, 255),
                  font=ImageFont.truetype(syst_bold, size=20), anchor="mm")

    # 面板数值
    draw.text((129, 201), attribute_values[0], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((258, 201), attribute_values[1], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((385, 201), attribute_values[2], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((514, 201), attribute_values[3], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((129, 278), attribute_values[4], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((258, 278), attribute_values[5], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((385, 278), attribute_values[6], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((514, 278), attribute_values[7], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((129, 355), attribute_values[8], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((258, 355), attribute_values[9], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((385, 355), attribute_values[10], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((514, 355), attribute_values[11], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")

    # 奇穴
    draw.text((320, 435), "奇穴", fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    init = 179
    limit = 0
    y = 479
    done_time = 0
    for i in qixue_icon:
        qximg = Image.open(await local_save(i)).resize((39, 39))
        background.alpha_composite(qximg, (init, y))
        init = init + 48
        limit = limit + 1
        if limit == 6:
            limit = 0
            init = 179
            y = 547
            done_time = done_time + 1
            if done_time == 2:
                break

    init = 199
    y = 530
    limit = 0
    done_time = 0
    for i in qixue_name:
        draw.text((init, y), i, file=(255, 255, 255),
                  font=ImageFont.truetype(msyh, size=12), anchor="mm")
        init = init + 48
        limit = limit + 1
        if limit == 6:
            limit = 0
            init = 199
            y = 598
            done_time = done_time + 1
            if done_time == 2:
                break

    # 装备位置
    init = 50
    equips = ["帽子", "上衣", "腰带", "护手", "下装", "鞋子", "项链", "腰坠", "戒指", "戒指", "远程武器", "近身武器"]
    for i in equips:
        draw.text((940, init), i, file=(255, 255, 255),
                  font=ImageFont.truetype(msyh, size=12), anchor="lt")
        init = init + 49

    # 五行石
    positions = [(940, 65), (960, 65), (940, 114), (960, 114), (940, 163), (960, 163), (940, 212), (960, 212), (940, 261),
                 (960, 261), (940, 310), (960, 310), (940, 359), (940, 408), (940, 555), (940, 604), (960, 604), (980, 604)]
    range_time = 18
    if kungfu.name in ["问水诀", "山居剑意"]:
        range_time = range_time + 3
        positions.append((940, 653))
        positions.append((960, 653))
        positions.append((980, 653))
    for i in range(range_time):
        background.alpha_composite(Image.open(five_stone[i]).resize((20, 20)), positions[i])

    # 小附魔
    init = 45
    for i in permanent_enchant:
        if i == "":
            init = init + 49
            continue
        else:
            background.alpha_composite(permanent_enchant_icon, (1044, init))
            draw.text((1068, init + 4), i, file=(255, 255, 255),
                      font=ImageFont.truetype(msyh, size=12), anchor="lt")
            init = init + 49

    # 大附魔
    y = [65, 114, 163, 212, 310]
    for i in range(5):
        if common_enchant[i] == "":
            continue
        else:
            background.alpha_composite(common_enchant_icon, (1044, y[i]))
            draw.text((1068, y[i] + 4), common_enchant[i], file=(255, 255, 255),
                      font=ImageFont.truetype(msyh, size=12), anchor="lt")

    # 五彩石
    if color_stone_icon != "":
        background.alpha_composite(Image.open(await local_save(color_stone_icon)).resize((20, 20)), (1044, 604))
    if color_stone_name != "":
        draw.text((1068, 608), color_stone_name, file=(255, 255, 255),
                  font=ImageFont.truetype(msyh, size=12), anchor="lt")
    if color_stone_icon_2 != "":
        background.alpha_composite(Image.open(await local_save(color_stone_icon_2)).resize((20, 20)), (1044, 654))
    if color_stone_name_2 != "":
        draw.text((1068, 657), color_stone_name_2, file=(255, 255, 255),
                  font=ImageFont.truetype(msyh, size=12), anchor="lt")

    final_path = build_path(CACHE, [get_uuid() + ".png"])
    background.save(final_path)
    return Path(final_path).as_uri()