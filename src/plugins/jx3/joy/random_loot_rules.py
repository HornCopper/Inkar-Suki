from dataclasses import dataclass


CHALLENGE_DUNGEONS = {
    "空城殿·上",
    "空城殿·下",
    "缚罪之渊",
    "阆风悬城·元心殿",
}

# 拆分成独立地图的首领，仍沿用双首领挑战本的对应序号规则。
CHALLENGE_BOSS_SLOT_OVERRIDES = {
    "空城殿·上": (1, 2),
    "空城殿·下": (2, 2),
}

CHALLENGE_DUNGEON_TOTALS = {
    "缚罪之渊": 2,
    "阆风悬城·元心殿": 2,
}


@dataclass(frozen=True)
class LootProbabilities:
    general_brand: int = 40
    weapon: int = 10
    jingjian: int = 10
    xuanjing: int = 1
    sand_material: int = 30
    other_peerless: int = 5
    appearance: int = 5
    extra_peerless: int = 10
    book: int = 5
    challenge_treasure_replacement: int = 20
    weapon_box_replacement: int = 20
    final_boss_box: int = 20

# 作弊工具
# @dataclass(frozen=True)
# class LootProbabilities:
#     general_brand: int = 100
#     weapon: int = 100
#     jingjian: int = 100
#     xuanjing: int = 100
#     sand_material: int = 100
#     other_peerless: int = 100
#     appearance: int = 100
#     extra_peerless: int = 100
#     book: int = 100
#     challenge_treasure_replacement: int = 100
#     weapon_box_replacement: int = 100
#     final_boss_box: int = 100


LOOT_PROBABILITIES = LootProbabilities()


@dataclass(frozen=True)
class BossLootRule:
    index: int
    total: int

    @property
    def is_final(self) -> bool:
        return self.index == self.total

    @property
    def is_penultimate(self) -> bool:
        return self.total > 1 and self.index == self.total - 1

    @property
    def is_penultimate_in_six(self) -> bool:
        return self.total == 6 and self.is_penultimate

    @property
    def is_penultimate_in_five(self) -> bool:
        return self.total == 5 and self.is_penultimate

    @property
    def position(self) -> str:
        return f"{self.index}/{self.total}"


def get_boss_loot_rule(
    dungeon_name: str,
    index: int,
    total: int,
) -> BossLootRule:
    short_name = dungeon_name.removeprefix("25人挑战")
    effective_index, effective_total = CHALLENGE_BOSS_SLOT_OVERRIDES.get(
        short_name,
        (index, CHALLENGE_DUNGEON_TOTALS.get(short_name, total)),
    )
    return BossLootRule(effective_index, effective_total)
