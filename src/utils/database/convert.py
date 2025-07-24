from typing import Any

Locations = ["武器", None, "暗器", "上衣", "帽子", "项链", "戒指", "戒指", "腰带", "腰坠", "下装", "鞋子", "护腕"]

class TuilanData:
    def __init__(self, tuilan_data: dict[str, Any]):
        self.tuilan_data = tuilan_data

    def unit_parse(self, equip_data: dict) -> list[int]:
        equip_type = equip_data["EquipType"]["SubType"]
        location_id = Locations.index(equip_type)
        index_type = int(equip_data["TabType"])
        index_id = int(equip_data["ID"])
        strength = int(equip_data["StrengthLevel"])
        fivestones = []
        for each_fivestone in equip_data.get("FiveStone", []):
            fivestone_data = [5, int(each_fivestone["Level"]) + 24441]
            fivestones.append(fivestone_data)
        if location_id == 0:
            if "ColorStone" in equip_data:
                fivestones.append(
                    [0, int(equip_data["ColorStone"]["ID"])]
                )
        p_enchant = 0
        c_enchant = 0
        if "WPermanentEnchant" in equip_data:
            p_enchant = int(equip_data["WPermanentEnchant"]["ID"])
        if "WCommonEnchant" in equip_data:
            c_enchant = int(equip_data["WCommonEnchant"]["ID"])
        final_data = [
            location_id,
            index_type,
            index_id,
            strength,
            fivestones,
            p_enchant,
            c_enchant,
            0
        ]
        return final_data

    def output_jcl_line(self):
        final_equip_data: list = []
        for each_equip in self.tuilan_data["data"]["Equips"]:
            equip_data = self.unit_parse(each_equip)
            final_equip_data.append(equip_data)
        return final_equip_data