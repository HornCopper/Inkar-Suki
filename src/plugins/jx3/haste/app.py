from math import ceil
from pathlib import Path

from jinja2 import Template

from src.const.path import ASSETS, TEMPLATES, build_path
from src.templates import get_saohua
from src.utils.database.constant import CURRENT_LEVEL, HASTE_DIVISOR
from src.utils.file import read
from src.utils.generate import generate


ORIGIN_FRAME = 24
FRAMES_PER_SECOND = 16
LIMITED_HASTE_CAP = 256


def get_haste_frame(origin_frame: int, haste_rate: float) -> int:
    return int((1024 * origin_frame) / (haste_rate + 1024))


def haste_rate_from_rating(rating: int) -> int:
    return int(rating / HASTE_DIVISOR * 1024)


def minimum_haste_rate(origin_frame: int, target_frame: int) -> int:
    if not 0 <= target_frame <= origin_frame:
        raise ValueError("目标帧数必须在 0 到基础帧数之间")
    if target_frame == origin_frame:
        return 0

    rate = max(0, origin_frame * 1024 // (target_frame + 1) - 1024 + 1)
    while get_haste_frame(origin_frame, rate) > target_frame:
        rate += 1
    while rate > 0 and get_haste_frame(origin_frame, rate - 1) <= target_frame:
        rate -= 1
    return rate


def minimum_haste_rating(rate: int) -> int:
    if rate <= 0:
        return 0
    low, high = 0, max(1, ceil(rate * HASTE_DIVISOR / 1024))
    while haste_rate_from_rating(high) < rate:
        high *= 2
    while low < high:
        middle = (low + high) // 2
        if haste_rate_from_rating(middle) >= rate:
            high = middle
        else:
            low = middle + 1
    return low


def effective_haste_rate(rating: int, addition_rate: int = 0, unlimited: bool = False) -> int:
    limited_rate = min(haste_rate_from_rating(rating), LIMITED_HASTE_CAP)
    if unlimited:
        return limited_rate + addition_rate
    return min(limited_rate + addition_rate, LIMITED_HASTE_CAP)


def haste_rows(
    origin_frame: int = ORIGIN_FRAME, addition_rate: int = 0, unlimited: bool = False,
) -> list[dict[str, str | int | bool]]:
    if origin_frame < 1 or addition_rate < 0:
        raise ValueError("基础帧数须为正整数，附加加速须为非负整数")
    rows = []
    max_rate = LIMITED_HASTE_CAP + addition_rate if unlimited else LIMITED_HASTE_CAP
    fastest_frame = get_haste_frame(origin_frame, max_rate)
    initial_frame = get_haste_frame(
        origin_frame, effective_haste_rate(0, addition_rate, unlimited),
    )
    for frame in range(initial_frame, fastest_frame - 1, -1):
        required_rate = minimum_haste_rate(origin_frame, frame)
        required_limited_rate = max(0, required_rate - addition_rate)
        rating = minimum_haste_rating(required_limited_rate)
        actual_frame = get_haste_frame(
            origin_frame, effective_haste_rate(rating, addition_rate, unlimited),
        )
        rows.append({
            "frame": frame,
            "seconds": f"{frame / FRAMES_PER_SECOND:.2f}",
            "rate": f"{rating / HASTE_DIVISOR * 100:.2f}",
            "rating": rating,
            "actual_frame": actual_frame,
            "skipped": actual_frame < frame,
        })
    return rows


async def render_haste_image(
    origin_frame: int = ORIGIN_FRAME, addition_rate: int = 0, unlimited: bool = False,
):
    rows = haste_rows(origin_frame, addition_rate, unlimited)
    html = Template(read(build_path(TEMPLATES, ["jx3", "haste.html"]))).render(
        font=Path(build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"])).as_uri(),
        level=CURRENT_LEVEL,
        origin_frame=origin_frame,
        addition_rate=addition_rate,
        unlimited=unlimited,
        rows=rows,
        saohua=get_saohua(),
    )
    return await generate(html, ".haste-report", segment=True)
