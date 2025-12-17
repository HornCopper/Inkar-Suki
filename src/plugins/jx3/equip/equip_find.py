from jinja2 import Template

from src.config import Config
from src.const.path import ASSETS, TEMPLATES
from src.utils.network import Request
from src.utils.database.constant import Colors, EquipLocations, StrengthIncome
from src.utils.database.attributes import TabCache
from src.utils.generate import generate
from src.utils.file import read
from src.plugins.jx3.calculator.compare import AttributesFull, subtype_locations

from ._template import _template_green_attrs, _template_diamonds, _template_set_attrs

async def get_equip_info(equip_name: str) -> list[tuple[str, dict]] | str:
    url = f"{Config.jx3.api.calculator_url}/equip?equip_name={equip_name}"
    results = []
    data = (await Request(url).get()).json()
    if len(data) == 0:
        return "未找到符合条件的装备，请检查装备名称！"
    else:
        for each_equip in data:
            attr_abbr = []
            color = "rgb" + Colors[int(each_equip["Quality"])]
            if int(each_equip["Quality"]) == 5:
                strength_income = 8
            else:
                strength_income = 6
            strength = "⭐️" * strength_income
            icon, name = TabCache.get_icon_for_equip(int(each_equip["UiID"]))
            icon = f"https://icon.jx3box.com/icon/{icon}.png"
            quality = each_equip["Level"]
            location = EquipLocations[subtype_locations[int(each_equip["SubType"])]]
            green_attrs = []
            skillevent = []
            for n in range(1, 20 + 1):
                if f"Magic{n}Key" not in each_equip or f"Magic{n}Value" not in each_equip:
                    break
                attr_key_name = each_equip[f"Magic{n}Key"]
                attr_value = each_equip[f"Magic{n}Value"]
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
                if f"DiamondAttributeID{n}Key" not in each_equip or f"DiamondAttributeID{n}Value" not in each_equip:
                    break
                attr_key_name = each_equip[f"DiamondAttributeID{n}Key"]
                attr_value = each_equip[f"DiamondAttributeID{n}Value"]
                attr_name = AttributesFull.get(attr_key_name, "未知属性")
                diamonds.append(
                    Template(_template_diamonds).render(
                        diamond_icon = ASSETS + "/image/jx3/attributes/wuxingshi/8.png",
                        attr_name = attr_name
                    )
                )
            final_set_attrs = []
            for set_count, set_attrs in each_equip["SetAttributes"].items():
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
            remark = "备注：" + each_equip["MagicType"] + "（" + each_equip["Index"] + "_" + each_equip["ID"] + "）"
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
            results.append(
                (f"{name}\n{quality} {' '.join(attr_abbr)}", result)
            )
        return results

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