from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import random
import re
import uuid

from PIL import Image

from src.const.path import ASSETS, CACHE


SUITS = "mps"
TERMINAL_HONORS = {0, 8, 9, 17, 18, 26, *range(27, 34)}
TILE_IMAGE_DIR = Path(ASSETS) / "image" / "mahjong"
FAKE_TENPAI_RATE = 0.2


@dataclass(frozen=True)
class TenpaiQuestion:
    hand: tuple[int, ...]
    waits: tuple[int, ...]
    hand_code: str


def tile_to_code(tile: int) -> str:
    if tile < 9:
        return f"{tile + 1}m"
    if tile < 18:
        return f"{tile - 8}p"
    if tile < 27:
        return f"{tile - 17}s"
    return f"{tile - 26}z"


def tiles_to_code(tiles: list[int] | tuple[int, ...]) -> str:
    parts: list[str] = []
    for suit_index, suit in enumerate(SUITS):
        base = suit_index * 9
        nums = "".join(str(tile - base + 1) for tile in sorted(tiles) if base <= tile < base + 9)
        if nums:
            parts.append(nums + suit)
    honors = "".join(str(tile - 26) for tile in sorted(tiles) if tile >= 27)
    if honors:
        parts.append(honors + "z")
    return "".join(parts)


def parse_tiles(text: str) -> list[int] | None:
    normalized = text.lower().replace(" ", "").replace(",", "").replace("，", "")
    if not normalized:
        return None

    tiles: list[int] = []
    pos = 0
    for match in re.finditer(r"([0-9]+)([mpsz])", normalized):
        if match.start() != pos:
            return None
        nums, suit = match.groups()
        if suit == "z":
            if any(num not in "1234567" for num in nums):
                return None
            tiles.extend(26 + int(num) for num in nums)
        else:
            if any(num not in "123456789" for num in nums):
                return None
            base = SUITS.index(suit) * 9
            tiles.extend(base + int(num) - 1 for num in nums)
        pos = match.end()

    if pos != len(normalized):
        return None
    return tiles


def _can_form_melds(counts: list[int], start: int = 0) -> bool:
    try:
        tile = next(i for i in range(start, 34) if counts[i])
    except StopIteration:
        return True

    if counts[tile] >= 3:
        counts[tile] -= 3
        if _can_form_melds(counts, tile):
            counts[tile] += 3
            return True
        counts[tile] += 3

    if tile < 27 and tile % 9 <= 6 and counts[tile + 1] and counts[tile + 2]:
        counts[tile] -= 1
        counts[tile + 1] -= 1
        counts[tile + 2] -= 1
        if _can_form_melds(counts, tile):
            counts[tile] += 1
            counts[tile + 1] += 1
            counts[tile + 2] += 1
            return True
        counts[tile] += 1
        counts[tile + 1] += 1
        counts[tile + 2] += 1

    return False


def is_standard_win(counts: list[int]) -> bool:
    for tile in range(34):
        if counts[tile] >= 2:
            counts[tile] -= 2
            if _can_form_melds(counts):
                counts[tile] += 2
                return True
            counts[tile] += 2
    return False


def is_chiitoi(counts: list[int]) -> bool:
    return sum(count == 2 for count in counts) == 7


def is_kokushi(counts: list[int]) -> bool:
    return all(counts[tile] for tile in TERMINAL_HONORS) and any(counts[tile] >= 2 for tile in TERMINAL_HONORS)


def is_win(tiles: list[int] | tuple[int, ...]) -> bool:
    if len(tiles) != 14:
        return False
    counts = [0] * 34
    for tile in tiles:
        counts[tile] += 1
        if counts[tile] > 4:
            return False
    return is_kokushi(counts) or is_chiitoi(counts) or is_standard_win(counts)


def get_waits(hand: list[int] | tuple[int, ...]) -> tuple[int, ...]:
    counts = Counter(hand)
    waits = [tile for tile in range(34) if counts[tile] < 4 and is_win([*hand, tile])]
    return tuple(waits)


def _random_standard_win() -> list[int]:
    for _ in range(5000):
        counts = [0] * 34
        pair = random.randrange(34)
        counts[pair] += 2
        tiles = [pair, pair]

        for _ in range(4):
            melds: list[tuple[int, int, int]] = []
            for tile in range(34):
                if counts[tile] <= 1:
                    melds.append((tile, tile, tile))
                if tile < 27 and tile % 9 <= 6 and all(counts[tile + offset] < 4 for offset in range(3)):
                    melds.append((tile, tile + 1, tile + 2))

            if not melds:
                break

            meld = random.choice(melds)
            for tile in meld:
                counts[tile] += 1
            tiles.extend(meld)
        else:
            return tiles

    raise RuntimeError("failed to generate standard winning hand")


def _random_chiitoi_win() -> list[int]:
    pairs = random.sample(range(34), 7)
    return [tile for tile in pairs for _ in range(2)]


def _random_kokushi_win() -> list[int]:
    tiles = list(TERMINAL_HONORS)
    tiles.append(random.choice(tiles))
    return tiles


def _random_chinitsu_win() -> list[int]:
    base = random.choice((0, 9, 18))
    for _ in range(5000):
        counts = [0] * 34
        pair = base + random.randrange(9)
        counts[pair] += 2
        tiles = [pair, pair]

        for _ in range(4):
            melds: list[tuple[int, int, int]] = []
            for offset in range(9):
                tile = base + offset
                if counts[tile] <= 1:
                    melds.append((tile, tile, tile))
                if offset <= 6 and all(counts[tile + sequence_offset] < 4 for sequence_offset in range(3)):
                    melds.append((tile, tile + 1, tile + 2))

            if not melds:
                break

            meld = random.choice(melds)
            for tile in meld:
                counts[tile] += 1
            tiles.extend(meld)
        else:
            return tiles

    raise RuntimeError("failed to generate chinitsu winning hand")


def _is_chinitsu(tiles: list[int] | tuple[int, ...]) -> bool:
    suited_tiles = [tile for tile in tiles if tile < 27]
    return len(suited_tiles) == len(tiles) and len({tile // 9 for tile in suited_tiles}) == 1


def _matches_difficulty(waits: tuple[int, ...], difficulty: str) -> bool:
    if difficulty == "hard":
        return 3 <= len(waits) < 13
    if difficulty == "chinitsu":
        return bool(waits)
    return bool(waits)


def _generate_real_question(difficulty: str = "simple") -> TenpaiQuestion:
    generators = [_random_standard_win] * 8 + [_random_chiitoi_win, _random_kokushi_win]
    if difficulty == "chinitsu":
        generators = [_random_chinitsu_win]
    attempts = 20000 if difficulty in {"hard", "chinitsu"} else 1000
    for _ in range(attempts):
        winning = random.choice(generators)()
        random.shuffle(winning)
        hand = winning.copy()
        hand.pop(random.randrange(len(hand)))
        hand.sort()
        waits = get_waits(hand)
        if difficulty == "chinitsu" and not _is_chinitsu(hand):
            continue
        if _matches_difficulty(waits, difficulty):
            return TenpaiQuestion(tuple(hand), waits, tiles_to_code(hand))

    raise RuntimeError("failed to generate tenpai question")


def _nearby_tile_candidates(tile: int, difficulty: str) -> list[int]:
    if difficulty == "chinitsu":
        base = tile // 9 * 9
        candidates = [base + offset for offset in range(9)]
    elif tile < 27:
        base = tile // 9 * 9
        candidates = [base + offset for offset in range(9)]
    else:
        candidates = list(range(27, 34))

    candidates.sort(key=lambda candidate: abs(candidate - tile))
    return candidates


def _generate_fake_question(difficulty: str = "simple") -> TenpaiQuestion:
    for _ in range(1000):
        question = _generate_real_question(difficulty)
        hand = list(question.hand)
        indices = list(range(len(hand)))
        random.shuffle(indices)
        for index in indices:
            original = hand[index]
            candidates = _nearby_tile_candidates(original, difficulty)
            candidates.extend(random.sample(range(34), 34))
            for replacement in candidates:
                if replacement == original:
                    continue
                candidate_hand = hand.copy()
                candidate_hand[index] = replacement
                if Counter(candidate_hand)[replacement] > 4:
                    continue
                candidate_hand.sort()
                if difficulty == "chinitsu" and not _is_chinitsu(candidate_hand):
                    continue
                if not get_waits(candidate_hand):
                    return TenpaiQuestion(tuple(candidate_hand), tuple(), tiles_to_code(candidate_hand))

    raise RuntimeError("failed to generate fake tenpai question")


def generate_question(difficulty: str = "simple") -> TenpaiQuestion:
    if random.random() < FAKE_TENPAI_RATE:
        return _generate_fake_question(difficulty)
    return _generate_real_question(difficulty)


def _tile_image_path(tile: int) -> Path:
    return TILE_IMAGE_DIR / f"{tile_to_code(tile)}.png"


def render_hand_image(tiles: list[int] | tuple[int, ...]) -> str:
    images = [Image.open(_tile_image_path(tile)).convert("RGBA") for tile in tiles]
    try:
        width = sum(image.width for image in images)
        height = max(image.height for image in images)
        canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        x = 0
        for image in images:
            canvas.alpha_composite(image, (x, height - image.height))
            x += image.width

        cache_dir = Path(CACHE)
        cache_dir.mkdir(parents=True, exist_ok=True)
        output_path = cache_dir / f"mahjong_tenpai_{uuid.uuid4().hex}.png"
        canvas.save(output_path, format="PNG")
        return str(output_path)
    finally:
        for image in images:
            image.close()


def is_correct_answer(answer: str, waits: tuple[int, ...]) -> bool:
    normalized_answer = answer.strip().lower().replace(" ", "")
    if normalized_answer in {"未听牌", "没听牌", "沒有听牌", "沒有聽牌", "未聽牌", "没聽牌", "noten"}:
        return not waits

    tiles = parse_tiles(answer)
    if tiles is None:
        return False

    actual = set(waits)
    guessed = set(tiles)
    if guessed == actual:
        return True

    kokushi_waits = tuple(sorted(TERMINAL_HONORS))
    if tuple(sorted(waits)) == kokushi_waits and set(tiles).issubset(TERMINAL_HONORS) and len(set(tiles)) >= 11:
        return True

    return False
