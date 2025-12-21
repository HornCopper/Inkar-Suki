from jinja2 import Template

from src.config import Config
from src.const.path import ASSETS, TEMPLATES
from src.utils.network import Request
from src.utils.database.constant import Colors, EquipLocations, StrengthIncome
from src.utils.database.attributes import TabCache
from src.utils.generate import generate
from src.utils.file import read
from src.plugins.jx3.calculator.compare import AttributesFull, subtype_locations

from src.plugins.jx3.equip._template import _template_green_attrs, _template_diamonds, _template_set_attrs

async def get_equip_info(params: dict) -> dict:
    url = f"{Config.jx3.api.calculator_url}/equip"
    equip = (await Request(url, params=params).get()).json()
    attr_abbr = []
    color = "rgb" + Colors[int(equip["Quality"])]
    if int(equip["Quality"]) == 5:
        strength_income = 8
    else:
        strength_income = 6
    strength = "⭐️" * strength_income
    icon, name = TabCache.get_icon_for_equip(int(equip["UiID"]))
    icon = f"https://icon.jx3box.com/icon/{icon}.png"
    quality = equip["Level"]
    location = EquipLocations[subtype_locations[int(equip["SubType"])]]
    green_attrs = []
    skillevent = []
    for n in range(1, 20 + 1):
        if f"Magic{n}Key" not in equip or f"Magic{n}Value" not in equip:
            break
        attr_key_name = equip[f"Magic{n}Key"]
        attr_value = equip[f"Magic{n}Value"]
        if attr_key_name == "atSkillEventHandler":
            skillevent.append(
                "· " + TabCache.get_effect_by_skill_handler_id(int(attr_value))
            )
            continue
        attr_name = AttributesFull.get(attr_key_name, "未知属性")
        if attr_name == "未知属性":
            continue
        attr_abbr.append(attr_name)
        green_attrs.append(
            Template(_template_green_attrs).render(
                attr_name = attr_name,
                attr_value = attr_value,
                strength_value = int(int(attr_value) * StrengthIncome[strength_income] + 0.5)
            )
        )
    diamonds = []
    for n in range(1, 3 + 1):
        if f"DiamondAttributeID{n}Key" not in equip or f"DiamondAttributeID{n}Value" not in equip:
            break
        attr_key_name = equip[f"DiamondAttributeID{n}Key"]
        attr_value = equip[f"DiamondAttributeID{n}Value"]
        attr_name = AttributesFull.get(attr_key_name, "未知属性")
        diamonds.append(
            Template(_template_diamonds).render(
                diamond_icon = ASSETS + "/image/jx3/attributes/wuxingshi/8.png",
                attr_name = attr_name
            )
        )
    final_set_attrs = []
    for set_count, set_attrs in equip["SetAttributes"].items():
        for set_attr in set_attrs:
            each_attr_key, each_attr_value = next(iter(set_attr.items()))
            if each_attr_key in AttributesFull:
                msg = f"{AttributesFull[each_attr_key]}提高{each_attr_value}点"
            elif each_attr_key == "atSkillEventHandler":
                msg = TabCache.get_effect_by_skill_handler_id(int(each_attr_value))
            else:
                msg = "未知效果(未解析)"
            final_set_attrs.append(
                Template(_template_set_attrs).render(
                    count = str(set_count),
                    attr = msg
                )
            )
    remark = "备注：" + equip["MagicType"] + "（" + equip["Index"] + "_" + equip["ID"] + "）"
    result = {
        "color": color,
        "name": name,
        "strength": strength,
        "icon": icon,
        "quality": quality,
        "location": location,
        "green_attrs": "\n".join(green_attrs),
        "diamonds": "\n".join(diamonds),
        "skillevent": "<br>".join(skillevent),
        "set": "\n".join(final_set_attrs),
        "remark": remark
    }
    return result

async def get_equip_info_image(info: dict):
    arguments = {
        "font": ASSETS + "/font/PingFangSC-Semibold.otf",
        **info
    }
    html = Template(
        read(TEMPLATES + "/jx3/equip.html")
    ).render(
        **arguments
    )
    return await generate(
        html,
        ".card",
        segment=True,
        wait_for_network=True,
        viewport={"height": 1080, "width": 1920},
    )