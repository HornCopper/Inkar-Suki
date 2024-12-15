from typing import Any

from src.utils.analyze import merge_dicts
from src.const.jx3.kungfu import Kungfu

def percent(v):
    return (f"{float(v[:-1]):.10g}".rstrip("0").rstrip(".") or "0") + "%"

def sum_attr(d: dict[str, float], a: str) -> float:
    return sum(value for key, value in d.items() if a in key)

def input_attr(keys: list[str], data_dict: dict[str, int | float | str]) -> list[str]:
    result = []
    for key in keys:
        if key in data_dict:
            value = data_dict[key]
            if not isinstance(value, str):
                value = str(int(value)) if isinstance(value, (int, float)) else str(value)
            result.append(value)
    return result

def mobile_attribute_calculator(equip_data: list[dict[str, Any]], kungfu_name: str, panel_types: list[str]) -> list[str]:
    attr: dict[str, float] = {
        "atSpiritBase": 44,
        "atStrengthBase": 44,
        "atAgilityBase": 44,
        "atSpunkBase": 44,
        "atVitalityBase": 45
    }
    affected_set: list[set] = []
    for each_equip in equip_data:
        if "FiveStone" in each_equip:
            for each_fivestone in each_equip["FiveStone"]:
                attr_name = each_fivestone["Desc"]
                attr_value = int(each_fivestone["IncreaseGeneratedMagic"])
                attr[attr_name] = attr.get(attr_name, 0) + attr_value
        if "effectColorStone" in each_equip:
            for each_attr in each_equip["effectColorStone"]["Attributes"]:
                attr_name = each_attr["Desc"]
                attr_value = float(each_attr["Attribute1Value1"])
                attr[attr_name] = attr.get(attr_name, 0) + attr_value
        if "WPermanentEnchant" in each_equip:
            for each_attr in each_equip["WPermanentEnchant"]["Attributes"]:
                attr_name = each_attr["Desc"]
                attr_value = float(each_attr["Attribute1Value1"])
                attr[attr_name] = attr.get(attr_name, 0) + attr_value
        if "Set" in each_equip and "SetListMap" in each_equip:
            if set(each_equip["SetListMap"]) not in affected_set:
                for set_attr in each_equip["Set"]:
                    if int(set_attr["SetNum"]) <= len(each_equip["SetListMap"]):
                        attr_name = set_attr["Desc"]
                        attr_value = float(set_attr["Param1Max"])
                        attr[attr_name] = attr.get(attr_name, 0) + attr_value
                        affected_set.append(set(each_equip["SetListMap"]))
        for each_attr in each_equip["ModifyType"]:
            attr_name = each_attr["Desc"]
            attr_value = float(each_attr["Param1Max"]) + float(each_attr["Increase"])
            attr[attr_name] = attr.get(attr_name, 0) + attr_value
    attr.pop("atSkillEventHandler", None) # 套装效果（施展招式）
    attr.pop("atSetEquipmentRecipe", None) # 套装效果（伤害提高）
    attr.pop("atPVXAllRound", None) # 煞笔全能
    for b in ["根骨", "力道", "元气", "身法"]:
        key = {
            "根骨": "atSpiritBase",
            "力道": "atStrengthBase",
            "身法": "atAgilityBase",
            "元气": "atSpunkBase"
        }[b]
        if key in attr:
            attr[key] += attr.get("atBasePotentialAdd", 0)
    kungfu = Kungfu(kungfu_name)
    base_type = kungfu.base
    if base_type is None:
        return ["N/A"] * 12
    final_base_type = "防御"
    if base_type != "防御":
        final_base_type = base_type
    if final_base_type == "治疗":
        final_base_type = "根骨"
    format_attr = {}
    if final_base_type != "防御":
        format_attr[final_base_type] = int(
            attr[
                {
                    "根骨": "atSpiritBase",
                    "力道": "atStrengthBase",
                    "身法": "atAgilityBase",
                    "元气": "atSpunkBase"
                }[final_base_type]
            ]
        )
    attr = merge_dicts(attr, Kungfu.kungfu_basic[kungfu_name])
    format_attr["加速"] = int(attr.get("atHasteBase", 0))
    format_attr["最大气血值"] = "N/A"
    format_attr["破招"] = int(attr.get("atSurplusValueBase", 0))
    if base_type in ["根骨", "元气", "力道", "身法"]:
        extra_attack: float = 0
        if base_type in ["根骨", "元气"]:
            extra_attack = attr["atSpunkBase"] * 0.181
        else:
            extra_attack = attr["atStrengthBase"] * 0.163
        basic_attack: float = (
            sum_attr(attr, "AttackPowerBase") + # 装备攻击力
            extra_attack # 基础属性攻击力（元气和力道）
        )
        format_attr["基础攻击"] = int(basic_attack)
        if base_type == "根骨":
            if kungfu_name in ["冰心诀", "莫问", "紫霞功"]:
                format_attr["面板攻击"] = int(basic_attack + attr.get("atSpiritBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][0])
                attr["atMagicCriticalStrike"] = attr.get("atMagicCriticalStrike", 0) + attr.get("atSpiritBase", 0) * (Kungfu.kungfu_coefficient[kungfu_name][1] + 0.9)
            else: # 无方 毒经
                format_attr["面板攻击"] = int(basic_attack + attr.get("atSpiritBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][0])
                attr["atMagicOvercome"] = attr.get("atMagicOvercome", 0) + attr.get("atSpiritBase", 0) * (Kungfu.kungfu_coefficient[kungfu_name][1] + 0.3)
        elif base_type == "元气":
            if kungfu_name in ["易筋经", "焚影圣诀", "周天功"]:
                format_attr["面板攻击"] = int(basic_attack + attr.get("atSpunkBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][0])
                attr["atMagicCriticalStrike"] = attr.get("atMagicCriticalStrike", 0) + attr.get("atSpunkBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][1]
                attr["atMagicOvercome"] = attr.get("atMagicOvercome", 0) + attr.get("atSpunkBase", 0) * 0.3
            elif kungfu_name == "天罗诡道":
                format_attr["面板攻击"] = int(basic_attack + attr.get("atSpunkBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][0])
                attr["atPhysicsCriticalStrike"] = attr.get("atPhysicsCriticalStrike", 0) + attr.get("atSpunkBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][1]
                attr["atMagicOvercome"] = attr.get("atMagicOvercome", 0) + attr.get("atSpunkBase", 0) * 0.3
            else: # 花间游
                format_attr["面板攻击"] = int(basic_attack + attr.get("atSpunkBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][0])
                attr["atMagicOvercome"] = attr.get("atMagicOvercome", 0) + attr.get("atSpunkBase", 0) * (Kungfu.kungfu_coefficient[kungfu_name][1] + 0.3)
        elif base_type == "身法":
            if kungfu_name in ["隐龙诀", "问水诀"]:
                format_attr["面板攻击"] = int(basic_attack + attr.get("atAgilityBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][0])
                attr["atPhysicsCriticalStrike"] = attr.get("atPhysicsCriticalStrike", 0) + attr.get("atAgilityBase", 0) * 0.9
                attr["atPhysicsOvercomeBase"] = attr.get("atPhysicsOvercomeBase", 0) + attr.get("atAgilityBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][1]
            else: # 分山劲 太虚剑意 凌海诀 山海心诀
                format_attr["面板攻击"] = int(basic_attack + attr.get("atAgilityBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][0])
                attr["atPhysicsCriticalStrike"] = attr.get("atPhysicsCriticalStrike", 0) + attr.get("atAgilityBase", 0) * (Kungfu.kungfu_coefficient[kungfu_name][1] + 0.9)
        else: # 力道
            if kungfu_name in ["孤锋诀", "惊羽诀"]:
                format_attr["面板攻击"] = int(basic_attack + attr.get("atStrengthBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][0])
                attr["atPhysicsCriticalStrike"] = attr.get("atPhysicsCriticalStrike", 0) + attr.get("atStrengthBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][1]
                attr["atPhysicsOvercomeBase"] = attr.get("atPhysicsOvercomeBase", 0) + attr.get("atStrengthBase", 0) * 0.3
            else: # 傲血战意 北傲诀 笑尘诀
                format_attr["面板攻击"] = int(basic_attack + attr.get("atStrengthBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][0])
                attr["atMagicOvercome"] = attr.get("atMagicOvercome", 0) + attr.get("atSpunkBase", 0) * (Kungfu.kungfu_coefficient[kungfu_name][1] + 0.3)
    else:
        if base_type == "治疗":
            format_attr["外功防御"] = "N/A"
            format_attr["内功防御"] = "N/A"
            format_attr["基础治疗量"] = int(attr.get("atTherapyPowerBase", 0))
            format_attr["面板治疗量"] = int(attr.get("atTherapyPowerBase", 0) + attr.get("atSpiritBase", 0) * Kungfu.kungfu_coefficient[kungfu_name][0])
            attr["atMagicCriticalStrike"] = attr.get("atMagicCriticalStrike", 0) + attr.get("atSpiritBase", 0) * (Kungfu.kungfu_coefficient[kungfu_name][1] + 0.9)
        else: # 防御
            effect_attr = {
                "铁牢律": "atPhysicsShieldBase",
                "洗髓经": "atMagicShield",
                "明尊琉璃体": "atDodge",
                "铁骨衣": "atParryBase"
            }
            format_attr["体质"] = str(int(attr.get("atVitalityBase", 0)))
            attr[effect_attr[kungfu_name]] = attr[effect_attr[kungfu_name]] + attr["atVitalityBase"] * Kungfu.kungfu_coefficient[kungfu_name][0]
            attr["atParryValueBase"] = attr.get("atParryValueBase", 0) + attr["atVitalityBase"] * Kungfu.kungfu_coefficient[kungfu_name][1]
            format_attr["外功防御"] = percent(str(round(attr["atPhysicsShieldBase"] / (attr["atPhysicsShieldBase"] + 126007.2), 4) * 100) + "%")
            format_attr["内功防御"] = percent(str(round(attr["atMagicShield"] / (attr["atMagicShield"] + 126007.2), 4) * 100) + "%")
            format_attr["招架"] = percent(str(round(attr.get("atParryBase", 0) / (attr.get("atParryBase", 0) + 107553.6) + 0.03, 4) * 100) + "%")
            format_attr["拆招"] = str(int(attr.get("atParryValueBase", 0)))
            format_attr["闪避"] = percent(str(round(attr.get("atDodge", 0) / (attr.get("atDodge", 0) + 91634.4), 4) * 100) + "%")
            format_attr["加速率"] = percent(str(round(attr["atHasteBase"] / 210078.0, 4) * 100) + "%")
    format_attr["会心"] = percent(str(round(sum_attr(attr, "CriticalStrike") / 197703.0 * 100, 2)) + "%")
    format_attr["会心效果"] = percent(str(round(sum_attr(attr, "CriticalDamagePowerBase") / 72844.2 * 100, 2) + 175) + "%")
    format_attr["破防"] = percent(str(round(sum_attr(attr, "Overcome") / 225957.6 * 100, 2)) + "%")
    format_attr["无双"] = percent(str(round(sum_attr(attr, "atStrainBase") / 133333.2 * 100, 2)) + "%")
    format_attr["御劲"] = percent(str(round(sum_attr(attr, "atToughnessBase") / 197703.0 * 100, 2)) + "%")
    decritical = sum_attr(attr, "atDecriticalDamagePowerBase")
    format_attr["化劲"] = percent(str(round(decritical / (decritical + 33046.2) + 0.099609375, 4) * 100) + "%")
    return input_attr(panel_types, format_attr)