from typing_extensions import Self
from pathlib import Path
from random import choice, sample, randrange
from jinja2 import Template

from src.const.jx3.dungeon import Dungeon
from src.const.path import ASSETS
from src.utils.network import cache_image
from src.utils.jx3_dungeons import find_dungeon, dungeon_by_id
from src.utils.jx3_loot import (
    LootKind, group_loot, equipment_slot, enchant_weight,
)
from src.utils.generate import generate
from src.utils.database.constant import CURRENT_LEVEL
from src.templates import SimpleHTML, get_saohua

from ._template import (
    template_loot,
    template_item,
    template_loot_horizontal,
    template_item_horizontal,
)

from .random_item import (
    JX3RandomItem,
    item_colors,
    get_random,
)
from .random_loot_rules import (
    LOOT_PROBABILITIES,
    get_boss_loot_rule,
)
from .random_loot_source import get_local_lua_boss_drops


current_dungeon = ["会战弓月城", "洛阳之战"]

class RandomLoot:

    @classmethod
    async def with_map_name(cls, map_name: str, map_mode: str) -> Self | None:
        dungeon = Dungeon(map_name, map_mode)
        name, mode = dungeon.name or map_name, dungeon.mode
        if mode is None:
            return None
        record = await find_dungeon(name, mode)
        if record is None:
            return None
        name = record["canonicalName"]
        return cls(
            record["id"],
            record["requiredLevel"] == CURRENT_LEVEL,
            name in current_dungeon,
            mode + name,
        )

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
            filter_string = [
                "阴性",
                "阳性",
                "阴阳",
                "毒性",
                "值",
                "成效",
                "体质",
                "等级",
                "混元性",
                "招式产生威胁",
                "水下呼吸时间",
                "抗摔系数",
                "马术气力上限",
                "气力上限",
            ]
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
        record = await dungeon_by_id(self.map_id)
        self.boss_list = {name: index for index, name in enumerate(record["bosses"], 1)} if record else {}

    async def get_loot_list(self):
        self.loot_list_raw = await get_local_lua_boss_drops(self.map_id)

    @staticmethod
    def _select_special_pool(
        simplified: list[dict],
        effects: list[dict],
        hit_probability: int,
        upgrade_probability: int,
        guaranteed: bool = False,
    ) -> tuple[list[dict], bool]:
        if not (simplified or effects):
            return [], False
        if not guaranteed and not get_random(hit_probability):
            return [], False
        if effects and get_random(upgrade_probability):
            return effects, True
        return simplified, False

    async def distribute(
        self,
        probability_multiplier: int = 1,
    ) -> dict[str, list[JX3RandomItem]]:
        await self.get_boss_list()
        await self.get_loot_list()
        probabilities = LOOT_PROBABILITIES.scaled(probability_multiplier)
        result: dict[str, list[JX3RandomItem]] = {}

        def append_item(boss, item, count = 1, sort_priority = 2):
            result[boss].append(
                JX3RandomItem(
                    icon = item["Icon"]["FileName"],
                    name = item["Name"],
                    attr = self._parse_attributes(item),
                    color = item_colors[int(item["Color"])],
                    count = count,
                    sort_priority = sort_priority,
                ),
            )

        def random_items(pool, count = 1, unique_kind = False):
            items = list(pool)
            selected = []
            slots = {}
            for _ in range(max(0, count)):
                if not items:
                    break
                item = choice(items)
                selected.append(item)
                slot = equipment_slot(item)
                items = [other for other in items if other["id"] != item["id"]]
                slots[slot] = slots.get(slot, 0) + 1
                if unique_kind or slot == (6, 1):
                    items = [other for other in items if equipment_slot(other) != slot]
                elif slots[slot] >= 2:
                    other_slots = [other for other in items if equipment_slot(other) != slot]
                    if other_slots:
                        items = other_slots
            return selected

        for idx, (boss_name, loot_list) in enumerate(self.loot_list_raw.items(), 1):
            result[boss_name] = []
            rule = get_boss_loot_rule(self.name, idx, len(self.loot_list_raw))
            is_challenge = self.name.startswith("25人挑战")
            is_normal = self.name.startswith("10人普通")
            pools = group_loot(loot_list)

            def maybe_drop(pool, probability, sort_priority = 2):
                if pool and get_random(probability):
                    append_item(boss_name, choice(pool), sort_priority = sort_priority)
                    return 1
                return 0

            maybe_drop(pools[LootKind.EXTRA_PEERLESS], probabilities.extra_peerless, 1)
            maybe_drop(pools[LootKind.PEERLESS], probabilities.other_peerless, 1)
            maybe_drop(pools[LootKind.APPEARANCE], probabilities.appearance, 1)

            weapons = pools[LootKind.WEAPON] + pools[LootKind.EFFECT_WEAPON]
            weapon_boxes = pools[LootKind.WEAPON_BOX]
            simplified = pools[LootKind.SIMPLIFIED]
            effects = pools[LootKind.EFFECT_EQUIP]
            final_boxes = pools[LootKind.FINAL_WEAPON_BOX]
            armor = pools[LootKind.ARMOR] + pools[LootKind.EQUIPMENT_BOX]
            gear_count = 0

            # Simplified gear and its effect upgrade share one category decision
            # for the whole boss. Fixed effect weapons and pendants use separate slots.
            special_pool, upgraded = self._select_special_pool(
                simplified,
                effects,
                probabilities.jingjian,
                probabilities.effect_upgrade,
                guaranteed = is_challenge or (rule.is_final and not is_normal),
            )
            special_count = 3 if is_challenge else 2 if rule.is_final and not is_normal else 1
            special_items = random_items(
                special_pool,
                special_count,
                unique_kind = rule.is_final and not is_challenge,
            )
            if (is_challenge and upgraded and special_items and pools[LootKind.TREASURE]
                    and get_random(probabilities.challenge_treasure_replacement)):
                special_items[0] = choice(pools[LootKind.TREASURE])
            for item in special_items:
                append_item(boss_name, item)
                gear_count += 1

            if not is_normal:
                if not rule.is_final or rule.position == "5/5":
                    brands = sample(pools[LootKind.BRAND], k = min(3, len(pools[LootKind.BRAND])))
                    if brands and pools[LootKind.GENERAL_BRAND] and get_random(probabilities.general_brand):
                        brands[randrange(len(brands))] = choice(pools[LootKind.GENERAL_BRAND])
                    for item in brands:
                        append_item(boss_name, item)

                if not is_challenge:
                    pendants = pools[LootKind.EFFECT_PENDANT]
                    if pendants and (rule.position in ("4/5", "6/6") or (
                            rule.position == "4/6" and get_random(probabilities.effect_pendant))):
                        append_item(boss_name, choice(pendants))
                        gear_count += 1

                    if not rule.is_final:
                        if rule.is_penultimate_in_six:
                            for item in random_items(weapons + weapon_boxes, 2):
                                append_item(boss_name, item)
                                gear_count += 1
                        elif get_random(probabilities.weapon):
                            pool = weapon_boxes if weapon_boxes and get_random(
                                probabilities.weapon_box_replacement,
                            ) else weapons
                            if pool or weapon_boxes:
                                append_item(boss_name, choice(pool or weapon_boxes))
                                gear_count += 1

                    if rule.is_final:
                        pool = final_boxes if final_boxes and get_random(probabilities.final_boss_box) else weapons
                        if pool or final_boxes:
                            append_item(boss_name, choice(pool or final_boxes))
                            gear_count += 1

                    target = 8 if rule.is_final and rule.total == 6 else 4
                    for item in random_items(armor, target - gear_count):
                        append_item(boss_name, item)

                if rule.is_penultimate_in_six or rule.is_final or rule.is_penultimate_in_five:
                    maybe_drop(pools[LootKind.CRAFT_MATERIAL], probabilities.sand_material)
                    maybe_drop(pools[LootKind.CRYSTAL], probabilities.xuanjing, 0)
                maybe_drop(pools[LootKind.BOOK], probabilities.book)

                # Keep the client container as the reward; its scripted contents
                # are not present in the local tables and must not be invented.
                if pools[LootKind.ENCHANT_BOX]:
                    for _ in range(2):
                        append_item(boss_name, choice(pools[LootKind.ENCHANT_BOX]))
                if is_challenge:
                    for item in random_items(pools[LootKind.PERMANENT_ENCHANT], 3 if rule.index == 1 else 5):
                        append_item(boss_name, item)
            else:
                gear_count += maybe_drop(weapons, probabilities.weapon)
                for item in random_items(armor, 3 - gear_count):
                    append_item(boss_name, item)
                maybe_drop(pools[LootKind.CRYSTAL], probabilities.xuanjing, 0)

            if pools[LootKind.IRON]:
                append_item(
                    boss_name,
                    choice(pools[LootKind.IRON]),
                    count = rule.index + 1 if is_challenge else 1,
                )
            enchants = pools[LootKind.TEMP_ENCHANT]
            if enchants:
                weighted = [item for item in enchants for _ in range(1 if is_normal else enchant_weight(item))]
                append_item(boss_name, choice(weighted))

            # Only draw stones listed for this boss. Weights preserve the
            # existing mode rules when the corresponding stone is available.
            stone_weights = {"5_21510": 3, "5_21511": 3, "5_24428": 2, "5_24447": 2}
            if is_challenge:
                stone_weights = {"5_21512": 3, "5_21513": 1}
            stones = [item for item in pools[LootKind.STONE] for _ in range(stone_weights.get(item["id"], 1))]
            if stones:
                for _ in range(1 if is_challenge else 2):
                    append_item(boss_name, choice(stones))
        return result


    async def generate(
        self,
        display_mode: str = "纵向",
        probability_multiplier: int = 1,
    ):
        data = await self.distribute(
            probability_multiplier = probability_multiplier,
        )
        horizontal = display_mode == "横向"
        item_template = template_item_horizontal if horizontal else template_item
        loot_template = template_loot_horizontal if horizontal else template_loot
        loots = []
        for boss_name, items in data.items():
            if boss_name == "池青川":
                boss_name = "池请川"
            items = sorted(
                items,
                key = lambda item: item.sort_priority,
            )
            loot_items = []
            include_xuanjing = any(item.sort_priority == 0 for item in items)
            for item in items:
                loot_items.append(
                    Template(item_template).render(
                        highlight = include_xuanjing,
                        icon = await cache_image(item.icon),
                        item_color = "rgb" + item.color,
                        item_name = item.name,
                        attr = item.attr,
                        count = item.count,
                    ),
                )
            loots.append(
                Template(loot_template).render(
                    highlight = include_xuanjing,
                    boss_name = boss_name,
                    items = "\n".join(loot_items),
                ),
            )
        html = str(
            SimpleHTML(
                "jx3",
                "dungeon_loots_horizontal" if horizontal else "dungeon_loots",
                font = Path(ASSETS, "font", "PingFangSC-Semibold.otf").as_uri(),
                dungeon_name = self.name,
                item_count = sum(len(items) for items in data.values()),
                saohua = get_saohua(),
                loots = "\n".join(loots),
            ),
        )
        return await generate(html, ".panel", segment = True)
