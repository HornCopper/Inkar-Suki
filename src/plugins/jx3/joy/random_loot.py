from typing import cast
from typing_extensions import Self
from random import choice, sample, randrange
from jinja2 import Template

from src.const.jx3.dungeon import Dungeon
from src.const.path import ASSETS, CONST
from src.utils.network import Request, cache_image
from src.utils.generate import generate
from src.utils.file import read, write
from src.templates import SimpleHTML

from ._template import (
    template_loot,
    template_item,
    template_loot_horizontal,
    template_item_horizontal,
)

from .random_item import (
    JX3RandomItem,
    item_colors,
    get_random
)
from .random_loot_rules import (
    CHALLENGE_DUNGEONS,
    LOOT_PROBABILITIES,
    get_boss_loot_rule,
)
from .random_loot_source import get_local_lua_boss_drops

import re
import os
import json

current_level = 130

current_dungeon = ["会战弓月城"]

class RandomLoot:
    @classmethod
    async def with_map_name(cls, map_name: str, map_mode: str) -> Self | None:
        dungeon = Dungeon(map_name, map_mode)
        name, mode = dungeon.name, dungeon.mode
        if (name is None) or (mode is None):
            return None
        is_supported_challenge = mode == "25人挑战" and name in CHALLENGE_DUNGEONS
        is_supported_regular = name in ["会战弓月城", "阆风悬城"] and not (
            name == "会战弓月城" and mode == "25人普通"
        )
        if not (is_supported_challenge or is_supported_regular or mode == "10人普通"):
            return None
        list_all_file = CONST + "/cache/random_loot_list_all.json"
        if os.path.exists(list_all_file):
            data = cast(dict, read(list_all_file, True))
        else:
            url = "https://m.pvp.xoyo.com/dungeon/list-all"
            data = (await Request(url).post(tuilan=True)).json()
            write(list_all_file, json.dumps(data, ensure_ascii=False))
        level_dungeons: list[dict] = data["data"]
        for dungeons in level_dungeons:
            level = int(dungeons["devide_level"])
            for dungeon in dungeons["devide_list"]:
                if int(dungeon["type"]) != 2:
                    continue
                for each_dungeon in dungeon["dungeon_infos"]:
                    if each_dungeon["name"] == name:
                        for each_mode in each_dungeon["maps"]:
                            if each_mode["mode"] == mode:
                                return cls(int(each_mode["map_id"]), level == current_level, name in current_dungeon, mode + name)
                            
    @staticmethod
    def _parse_attributes(data: dict) -> str:
        msg = ""
        if "ModifyType" not in data:
            return ""
        for i in data["ModifyType"]:
            content = i["Attrib"]["GeneratedMagic"].split("提高")
            if len(content) == 1:
                content = content[0].split("增加")
            attr = content[0]
            attr = attr.replace("外功防御", "外防")
            attr = attr.replace("内功防御", "内防")
            filter_string = ["阴性", "阳性", "阴阳", "毒性", "值", "成效", "体质", "等级", "混元性", "招式产生威胁", "水下呼吸时间", "抗摔系数", "马术气力上限", "气力上限"]
            for y in filter_string:
                attr = attr.replace(y, "")
            if attr != "" and len(attr) <= 6:
                msg = msg + f" {attr}"
        msg = msg.replace(" 能 ", " 全能 ").replace(" 能", " 全能")
        return msg.strip()

    def __init__(self, map_id: int, is_current_level: bool, is_current_season: bool, name: str):
        self.name = name
        self.map_id = map_id
        self.is_current_level = is_current_level
        self.is_current_season = is_current_season
        self.boss_list: dict[str, int] = {}
        self.loot_list_raw: dict[str, list[dict]] = {}
        self.loot_list: dict[str, list[JX3RandomItem]] = {}

    async def get_boss_list(self):
        map_id = str(self.map_id)
        info_cache = CONST + f"/cache/random_loot_info_{map_id}.json"
        if os.path.exists(info_cache):
            data = cast(dict, read(info_cache, True))
        else:
            url = "https://m.pvp.xoyo.com/dungeon/info"
            params = {
                "map_id": map_id
            }
            data = (await Request(url, params=params).post(tuilan=True)).json()
            write(info_cache, json.dumps(data, ensure_ascii=False))
        bosses: list[dict] = data["data"]["info"]["boss_infos"]
        self.boss_list = {b["name"]: int(b["index"]) for b in bosses}
    
    async def get_loot_list(self):
        local_drops = get_local_lua_boss_drops(self.map_id)
        if local_drops:
            # 首领顺序以推栏为准，实际掉落池只使用本地 Lua 和 TAB 数据。
            self.loot_list_raw = {
                boss_name: local_drops[boss_name]
                for boss_name in self.boss_list
                if boss_name in local_drops
            }
            self.loot_list_raw.update(
                {
                    boss_name: items
                    for boss_name, items in local_drops.items()
                    if boss_name not in self.loot_list_raw
                }
            )
            return

        api_items_by_boss: dict[str, list[dict]] = {}
        for boss_name, boss_id in self.boss_list.items():
            info_cache = CONST + f"/cache/random_loot_boss_{boss_id}.json"
            if os.path.exists(info_cache):
                raw_data = cast(dict, read(info_cache, True))
                data = raw_data["data"]
            else:
                url = "https://m.pvp.xoyo.com/dungeon/boss-drop"
                params = {
                    "boss_id": boss_id,
                    "kungfu_list": []
                }
                raw_data = ((await Request(url, params=params).post(tuilan=True)).json())
                write(info_cache, json.dumps(raw_data, ensure_ascii=False))
                data = raw_data["data"]
            all_items_raw: list[dict] = data.get("armors", []) + data.get("weapons", []) + data.get("others", [])
            api_items_by_boss[boss_name] = all_items_raw
        self.loot_list_raw = api_items_by_boss
        
    async def distribute(self) -> dict[str, list[JX3RandomItem]]:
        await self.get_boss_list()
        await self.get_loot_list()
        result: dict[str, list[JX3RandomItem]] = {}

        def append_item(
            boss: str,
            item: dict,
            with_attr: bool = True,
            sort_priority: int = 2,
        ):
            kwargs = {
                "icon": item["Icon"]["FileName"],
                "name": item["Name"],
                "sort_priority": sort_priority,
            }
            if with_attr and "Color" in item:
                kwargs["attr"] = self._parse_attributes(item)
                kwargs["color"] = item_colors[int(item["Color"])]
            result[boss].append(JX3RandomItem(**kwargs))


        def random_items(filter_func, count=1, unique_kind: bool = False):
            items = []
            for i in loot_list:
                if filter_func(i):
                    items.append(i)

            if not items:
                return []
            
            sum = {}

            result = []
            for _ in range(count):
                if not items:
                    return result
                equip = choice(items)
                equip_kind = (
                    equip.get("SubType", equip["Icon"]["SubKind"])
                    if equip.get("BelongSchool") == "精简"
                    else equip["Icon"]["SubKind"]
                )
                items = [i for i in items if i.get("Name") != equip.get("Name")]
                if unique_kind:
                    items = [
                        i for i in items
                        if (
                            i.get("SubType", i["Icon"]["SubKind"])
                            if i.get("BelongSchool") == "精简"
                            else i["Icon"]["SubKind"]
                        ) != equip_kind
                    ]
                if equip_kind not in sum:
                    sum[equip_kind] = 0
                if equip_kind == "投掷囊":
                    items = [i for i in items if i["Icon"]["SubKind"] != "投掷囊"]
                sum[equip_kind] += 1
                if sum[equip_kind] == 2:
                    other_kind_items = [i for i in items if i["Icon"]["SubKind"] != equip_kind]
                    if other_kind_items:
                        items = other_kind_items
                
                result.append(equip)

            return result

        for idx, (boss_name, loot_list) in enumerate(self.loot_list_raw.items()):
            count = 0
            result[boss_name] = []
            total_boss = len(self.loot_list_raw)
            rule = get_boss_loot_rule(self.name, idx + 1, total_boss)
            boss_place = rule.position

            is_final = rule.is_final
            is_penultimate_6 = rule.is_penultimate_in_six
            is_penultimate_5 = rule.is_penultimate_in_five
            is_challenge = self.name.startswith("25人挑战")

            _general_brand = get_random(LOOT_PROBABILITIES.general_brand)
            _weapon = get_random(LOOT_PROBABILITIES.weapon)
            _jingjian = get_random(LOOT_PROBABILITIES.jingjian)
            _xuanjing = get_random(LOOT_PROBABILITIES.xuanjing)
            _sand_material = get_random(LOOT_PROBABILITIES.sand_material)
            _other_peerless = get_random(LOOT_PROBABILITIES.other_peerless) # 特殊掉落
            _appearance = get_random(LOOT_PROBABILITIES.appearance) # 外观道具
            _extra_peerless = get_random(LOOT_PROBABILITIES.extra_peerless) # 额外特殊掉落 例如阅读的书
            _book = get_random(LOOT_PROBABILITIES.book) # 侠客秘籍
        
            enchants = [i for i in loot_list if re.search(r'(伤|疗|御)·(腕|腰|鞋|帽|衣)$', str(i["Name"])) is not None]

            def has_readable_attributes(item: dict) -> bool:
                return any(
                    modify.get("Attrib", {}).get("GeneratedMagic")
                    for modify in item.get("ModifyType", [])
                )

            other_peerless_item = [
                i for i in loot_list
                if (
                    i.get("BelongSchool") == ""
                    and (
                        (
                            "ModifyType" in i
                            and not has_readable_attributes(i)
                        )
                        or (
                            "ModifyType" not in i
                            and i.get("Type") == ""
                        )
                    )
                )
                or i.get("Type") == "玩具"
                or "宠物" in str(i.get("Type", ""))
            ]
            appearance_items = [
                i for i in loot_list
                if i.get("Type") == "Act_运营及版本道具"
            ]
            extra_peerless_item = [i for i in loot_list if i.get("Type") in ["特殊武器任务", "阅读材料"]]
            iron = [i for i in loot_list if i["Name"].endswith("陨铁")]

            if is_challenge:
                def generated_attributes(item: dict) -> list[str]:
                    return [
                        str(modify.get("Attrib", {}).get("GeneratedMagic", ""))
                        for modify in item.get("ModifyType", [])
                    ]

                def is_heal_or_tank(item: dict) -> bool:
                    attributes = generated_attributes(item)
                    return any(
                        "治疗成效" in attr
                        or "御劲" in attr
                        or "招式产生威胁" in attr
                        for attr in attributes
                    )

                yellow_dps = [
                    item for item in loot_list
                    if item.get("BelongSchool") == "精简"
                    and "·" not in str(item.get("Name", ""))
                    and not is_heal_or_tank(item)
                ]
                heal_or_tank_effect = [
                    item for item in loot_list
                    if item.get("BelongSchool") == "精简"
                    and "·" not in str(item.get("Name", ""))
                    and is_heal_or_tank(item)
                ]
                non_yellow_dps = [
                    item for item in loot_list
                    if item.get("BelongSchool") == "精简"
                    and "·" in str(item.get("Name", ""))
                ]
                treasure_boxes = [
                    item for item in loot_list
                    if str(item.get("Name", "")).startswith("秘境宝藏")
                ]

                yellow_pool = treasure_boxes if get_random(
                    LOOT_PROBABILITIES.challenge_treasure_replacement
                ) and treasure_boxes else yellow_dps
                for pool in (yellow_pool, heal_or_tank_effect, non_yellow_dps):
                    if pool:
                        append_item(boss_name, choice(pool))

            if not self.name.startswith("10人普通"):
                if _extra_peerless and extra_peerless_item:
                    append_item(
                        boss_name,
                        choice(extra_peerless_item),
                        sort_priority=1,
                    )
                if _other_peerless:
                    if other_peerless_item:
                        append_item(
                            boss_name,
                            choice(other_peerless_item),
                            sort_priority=1,
                        )
                if _appearance and appearance_items:
                    append_item(
                        boss_name,
                        choice(appearance_items),
                        sort_priority=1,
                    )

                if not is_final or boss_place == "5/5":
                    brands = [i for i in loot_list if i.get("Type") == "副本掉落道具" and str(i["Name"]).count("·") == 1]
                    general_brands = [i for i in loot_list if str(i["Name"]).startswith("神兵玉匣") and str(i["Name"]).count("·") == 1]
                    selected_brands = sample(brands, k=min(3, len(brands))) if brands else []
                    if general_brands and selected_brands and _general_brand:
                        idx = randrange(len(selected_brands))
                        selected_brands[idx] = general_brands[0]
                    for item in selected_brands:
                        append_item(boss_name, item, with_attr=False)

                if not is_challenge and not is_penultimate_6 and _weapon and not is_final:
                    weapons = [i for i in loot_list if ("Color" in i and i.get("BelongSchool") not in ["精简", "通用", "藏剑", ""]) or str(i["Name"]).startswith("藏剑武器")]
                    weapon_boxes = [i for i in loot_list if not str(i["Name"]).startswith("于阗玉") and str(i["Name"]).count("·") == 2]
                    selected_pool = weapon_boxes if get_random(
                        LOOT_PROBABILITIES.weapon_box_replacement
                    ) and weapon_boxes else weapons
                    if not selected_pool:
                        selected_pool = weapon_boxes
                    if selected_pool:
                        append_item(boss_name, choice(selected_pool))
                        count += 1

                if not is_challenge and is_penultimate_6:
                    weapon_pool = [i for i in loot_list if ("Color" in i or str(i["Name"]).count("·") == 2)]
                    for item in random_items(lambda i: i in weapon_pool, 2):
                        append_item(boss_name, item, with_attr="Color" in item)
                    count += 2
                
                if not is_challenge and is_penultimate_5:
                    suits = [i for i in loot_list if "Color" in i and str(i.get("Desc")).startswith("使用：") and str(i.get("BelongSchool")) != ""] 
                    if suits:
                        append_item(boss_name, choice(suits))
                        count += 1

                # 精简
                if not is_challenge and not is_final and _jingjian:
                    jingjian_list = [i for i in loot_list if i.get("BelongSchool") == "精简" or ("Color" in i and str(i.get("Desc")).startswith("使用："))]
                    if jingjian_list:
                        append_item(boss_name, choice(jingjian_list))
                        count += 1

                # 散件（非最终）
                if not is_challenge and not is_final:
                    total = 4
                    sanjian_list = [i for i in loot_list if "ModifyType" in i and "Color" in i and i.get("BelongSchool") == "通用" and not str(i.get("Desc")).startswith("使用：")]
                    needed = total - count
                    for item in random_items(lambda i: i in sanjian_list, needed):
                        append_item(boss_name, item)

                # 最终 boss 特殊掉落
                if not is_challenge and is_final:
                    # 水特效
                    is_box = get_random(LOOT_PROBABILITIES.final_boss_box)
                    if is_box:
                        box = [i for i in loot_list if str(i["Name"]).endswith("·奇")]
                        if box:
                            append_item(boss_name, box[0])
                    else:
                        weapons = [i for i in loot_list if ("ModifyType" in i and i.get("Icon", {}).get("Kind") == "武器" and i.get("Icon", {}).get("SubKind") != "投掷囊") or str(i.get("Name")).startswith("藏剑武器·")]
                        if weapons:
                            append_item(boss_name, choice(weapons))
                    
                    # 腰坠
                    suits = [i for i in loot_list if "Color" in i and str(i.get("Desc")).startswith("使用：") and str(i.get("BelongSchool")) != ""] 
                    if suits:
                        append_item(boss_name, choice(suits))

                    # 精简 2件
                    if not self.name.startswith("25人挑战"):
                        jingjian_list = [i for i in loot_list if i.get("BelongSchool") == "精简"]
                        selected_jingjian = random_items(
                            lambda i: i in jingjian_list,
                            2,
                            unique_kind=True,
                        )
                        jingjian_count = len(selected_jingjian)
                        for item in selected_jingjian:
                            append_item(boss_name, item)
                    else:
                        special_jingjian_list = [i for i in loot_list if i.get("BelongSchool") == "精简" and "·" not in i.get("Name", "")]
                        common_jingjian_list = [i for i in loot_list if i.get("BelongSchool") == "精简" and "·" in i.get("Name", "")]
                        tn_special_list = [i for i in loot_list if i.get("BelongSchool") in ["防御", "治疗"]]
                        jingjian_count = 0
                        for pool in (
                            special_jingjian_list,
                            common_jingjian_list,
                            tn_special_list,
                        ):
                            if pool:
                                append_item(boss_name, choice(pool))
                                jingjian_count += 1

                    # 散件补满到8
                    if total_boss == 6:
                        sanjian_list = [i for i in loot_list if "ModifyType" in i and "Color" in i and i.get("BelongSchool") == "通用" and not str(i.get("Desc")).startswith("使用：")]
                        for item in random_items(lambda i: i in sanjian_list, 8 - 2 - jingjian_count):
                            append_item(boss_name, item)
                    else:
                        sanjian_list = [i for i in loot_list if "ModifyType" in i and "Color" in i and i.get("BelongSchool") == "通用" and not str(i.get("Desc")).startswith("使用：")]
                        for item in random_items(lambda i: i in sanjian_list, max(0, 4 - 1 - jingjian_count)):
                            append_item(boss_name, item)

                # 材料（5/6、6/6 特殊物资）
                if is_penultimate_6 or is_final or is_penultimate_5:
                    sand = [i for i in loot_list if i.get("Type") == "130级生活技能" and "·" not in i["Name"]]
                    if _sand_material and sand:
                        append_item(boss_name, sand[0], with_attr=False)

                    xuanjing = [i for i in loot_list if "玄晶" in i["Name"]]
                    if _xuanjing and xuanjing:
                        result[boss_name].append(JX3RandomItem(
                            icon=xuanjing[0]["Icon"]["FileName"],
                            name=xuanjing[0]["Name"],
                            color=item_colors[5]
                        ))
                
                if _book:
                    book_list = [i for i in loot_list if i.get("Type") == "红尘侠影" and str(i["Name"]).startswith("《")]
                    if book_list:
                        book = choice(book_list)
                        result[boss_name].append(JX3RandomItem(
                            icon=book["Icon"]["FileName"],
                            name=book["Name"],
                            color=item_colors[4]
                        ))

                # 陨铁
                if iron:
                    result[boss_name].append(JX3RandomItem(
                        icon=iron[0]["Icon"]["FileName"],
                        name=iron[0]["Name"],
                        color=item_colors[4],
                        count=rule.index + 1 if is_challenge else 1,
                    ))


                # 附魔
                if enchants:
                    final_enchants = []
                    for enchant in enchants:
                        if "伤" in enchant["Name"]:
                            final_enchants.append(enchant)
                            final_enchants.append(enchant)
                            final_enchants.append(enchant)
                        else:
                            final_enchants.append(enchant)
                    random_enchant = choice(final_enchants)
                    result[boss_name].append(
                        JX3RandomItem(
                            icon=random_enchant["Icon"]["FileName"],
                            name=random_enchant["Name"],
                            color=item_colors[4]
                        )
                    )
                
                
                if "昆仑玄石·附魔" in [str(i.get("Name")) for i in loot_list]:
                    icon = "https://icon.jx3box.com/icon/4432.png"
                    permanent_enchants = [
                        ("项链", "体质"),
                        ("项链", "御劲"),
                        ("腰坠", "体质"),
                        ("腰坠", "化劲"),
                        ("戒指", "根骨"),
                        ("戒指", "元气"),
                        ("戒指", "力道"),
                        ("戒指", "身法"),
                        ("戒指", "内攻"),
                        ("戒指", "外伤"),
                        ("戒指", "破招"),
                        ("暗器", "根骨"),
                        ("暗器", "元气"),
                        ("暗器", "力道"),
                        ("暗器", "身法"),
                        ("暗器", "加速"),
                        ("暗器", "内破"),
                        ("暗器", "外破")
                    ]
                    for _ in range(2):
                        location, attr = choice(permanent_enchants)
                        name = f"昆仑玄石·{location}（{attr}）"
                        result[boss_name].append(
                            JX3RandomItem(
                                icon=icon,
                                name=name
                            )
                        )

                if is_challenge:
                    permanent_enchants = [
                        item for item in loot_list
                        if item.get("Type") == "130级生活技能"
                        and "（" in str(item.get("Name", ""))
                        and str(item.get("Name", "")).endswith("）")
                    ]
                    enchant_count = 3 if rule.index == 1 else 5
                    selected_enchants = sample(
                        permanent_enchants,
                        k=min(enchant_count, len(permanent_enchants)),
                    )
                    for enchant in selected_enchants:
                        append_item(boss_name, enchant, with_attr=False)

                # 五彩石
                if self.name.startswith("25人挑战"):
                    materials = [
                        ("伍级五彩石", "https://icon.jx3box.com/icon/2330.png", 4),
                        ("伍级五彩石", "https://icon.jx3box.com/icon/2330.png", 4),
                        ("伍级五彩石", "https://icon.jx3box.com/icon/2330.png", 4),
                        ("陆级五彩石", "https://icon.jx3box.com/icon/2361.png", 4)
                    ]
                else:
                    materials = [
                        ("伍级五彩石", "https://icon.jx3box.com/icon/2330.png", 4),
                        ("肆级五彩石", "https://icon.jx3box.com/icon/2359.png", 3),
                        ("肆级五彩石", "https://icon.jx3box.com/icon/2359.png", 3),
                        ("肆级五彩石", "https://icon.jx3box.com/icon/2359.png", 3),
                        ("五行石（六级）", "https://icon.jx3box.com/icon/7528.png", 4),
                        ("五行石（六级）", "https://icon.jx3box.com/icon/7528.png", 4)
                    ]
                for _ in range(1 if self.name.startswith("25人挑战") else 2):
                    name, icon_url, color_id = choice(materials)
                    result[boss_name].append(
                        JX3RandomItem(
                            icon=icon_url,
                            name=name,
                            color=item_colors[color_id]
                        )
                    )
            else:
                if _extra_peerless and extra_peerless_item:
                    append_item(
                        boss_name,
                        choice(extra_peerless_item),
                        sort_priority=1,
                    )
                if _other_peerless and other_peerless_item: # 挂件 马 马具 等
                    append_item(
                        boss_name,
                        choice(other_peerless_item),
                        sort_priority=1,
                    )
                if _appearance and appearance_items:
                    append_item(
                        boss_name,
                        choice(appearance_items),
                        sort_priority=1,
                    )

                if _weapon:
                    weapons = [i for i in loot_list if ("Color" in i and i.get("BelongSchool") not in ["精简", "通用", "藏剑", ""]) or str(i["Name"]).startswith("藏剑武器")]
                    if weapons:
                        append_item(boss_name, choice(weapons))
                        count += 1
                    
                sanjian_list = [
                    i for i in loot_list
                    if "ModifyType" in i
                    and "Color" in i
                    and i.get("BelongSchool") == "通用"
                    and not str(i.get("Desc")).startswith("使用：")
                    and not str(i.get("Name")).startswith("探幽宝藏")
                ]

                for _ in range(3 - count):
                    append_item(boss_name, choice(sanjian_list))

                if iron:
                    result[boss_name].append(JX3RandomItem(
                        icon=iron[0]["Icon"]["FileName"],
                        name=iron[0]["Name"],
                        color=item_colors[4]
                    ))

                if enchants:
                    random_enchant = choice(enchants)
                    result[boss_name].append(
                        JX3RandomItem(
                            icon=random_enchant["Icon"]["FileName"],
                            name=random_enchant["Name"],
                            color=item_colors[4]
                        )
                    )

                if _xuanjing:
                    for item in loot_list:
                        if str(item.get("Name", "")).endswith("玄晶"):
                            result[boss_name].append(
                                JX3RandomItem(
                                    icon=item["Icon"]["FileName"],
                                    name=item["Name"],
                                    color=item_colors[5]
                                )
                            )
                
                materials = [
                    ("叁级五彩石", "https://icon.jx3box.com/icon/2348.png", 3),
                    ("叁级五彩石", "https://icon.jx3box.com/icon/2348.png", 3),
                    ("叁级五彩石", "https://icon.jx3box.com/icon/2348.png", 3),
                    ("肆级五彩石", "https://icon.jx3box.com/icon/2359.png", 3),
                    ("肆级五彩石", "https://icon.jx3box.com/icon/2359.png", 3),
                    ("肆级五彩石", "https://icon.jx3box.com/icon/2359.png", 3),
                    ("五行石（六级）", "https://icon.jx3box.com/icon/7528.png", 4),
                    ("五行石（六级）", "https://icon.jx3box.com/icon/7528.png", 4)
                ]
                for _ in range(2):
                    name, icon_url, color_id = choice(materials)
                    result[boss_name].append(
                        JX3RandomItem(
                            icon=icon_url,
                            name=name,
                            color=item_colors[color_id]
                        )
                    )

        return result
    
    async def generate(self, display_mode: str = "纵向"):
        data = await self.distribute()
        horizontal = display_mode == "横向"
        item_template = template_item_horizontal if horizontal else template_item
        loot_template = template_loot_horizontal if horizontal else template_loot
        loots = []
        for boss_name, items in data.items():
            if boss_name == "池青川":
                boss_name = "池请川"
            items = sorted(
                items,
                key=lambda item: (
                    0 if "玄晶" in item.name else item.sort_priority
                ),
            )
            loot_items = []
            include_xuanjing = any("玄晶" in s for s in [i.name for i in items])
            for item in items:
                loot_items.append(
                    Template(item_template).render(
                        highlight = include_xuanjing,
                        icon = await cache_image(item.icon),
                        item_color = "rgb" + item.color,
                        item_name = item.name,
                        attr = item.attr,
                        count = item.count,
                    )
                )
            loots.append(
                Template(loot_template).render(
                    highlight = include_xuanjing,
                    boss_name = boss_name,
                    items = "\n".join(loot_items)
                )
            )
        html = str(
            SimpleHTML(
                "jx3",
                "dungeon_loots_horizontal" if horizontal else "dungeon_loots",
                font = ASSETS + "/font/PingFangSC-Semibold.otf",
                dungeon_name = self.name,
                item_count = sum(len(items) for items in data.values()),
                loots = "\n".join(loots)
            )
        )
        return await generate(html, ".panel", segment=True)
