"""Fast, deterministic placement using image statistics, with no model or OCR."""
from dataclasses import dataclass, replace
import io
import time

import numpy as np
from PIL import Image, ImageOps


MAX_CARD_PIXELS = 16_000_000
MAX_UPSCALE = 4.0
UPSCALE_PIXEL_BUDGET = 4_000_000
UPSCALE_EDGE_LIMIT = 2560
# Size ratios scale with the card, constrained by both width and height.
SIZE_RATIOS = {'小': .27, '中': .36, '大': .45, '特大': .54}


@dataclass(frozen=True)
class Placement:
    left: int
    top: int
    width: int
    height: int
    score: float
    analysis_ms: float
    output_scale: float = 1.0


def _integral(values: np.ndarray) -> np.ndarray:
    return np.pad(values, ((1, 0), (1, 0))).cumsum(0).cumsum(1)


def _box_mean(values: np.ndarray, radius: int) -> np.ndarray:
    integral = _integral(np.pad(values, radius, mode='edge'))
    side = radius * 2 + 1
    return (integral[side:, side:] - integral[:-side, side:]
            - integral[side:, :-side] + integral[:-side, :-side]) / (side * side)


def find_placement(card: Image.Image, aspect: float = 522 / 500, *, size: str = '中') -> Placement:
    """Score a bounded thumbnail, then scan rectangles via integral images.

    Detailed regions (including text), skin-like colors and the likely head
    region cost more than low-detail background. This is a placement heuristic,
    not semantic face detection. All coordinates refer to the original image.
    """
    started = time.perf_counter()
    if size not in SIZE_RATIOS:
        raise ValueError('尺寸只能选择特大、大、中、小。')
    ratio = SIZE_RATIOS[size]
    original_width, original_height = card.size
    if min(card.size) < 64 or original_width * original_height > MAX_CARD_PIXELS:
        raise ValueError('名片尺寸不支持，请使用至少 64×64 且不超过 1600 万像素的图片。')
    thumbnail = card.convert('RGB')
    thumbnail.thumbnail((256, 256), Image.Resampling.BILINEAR)
    rgb = np.asarray(thumbnail, dtype=np.float32)
    height, width = rgb.shape[:2]
    gray = (rgb[:, :, 0] * .299 + rgb[:, :, 1] * .587 + rgb[:, :, 2] * .114) / 255
    mean = _box_mean(gray, 3)
    deviation = np.sqrt(np.maximum(_box_mean(gray * gray, 3) - mean * mean, 0))
    dy, dx = np.gradient(gray)
    edges = np.hypot(dx, dy)
    texture = np.clip(deviation / .10, 0, 1)
    edge_density = _box_mean(np.clip(edges / .12, 0, 1), 2)

    red, green, blue = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    cb = 128 - .168736 * red - .331264 * green + .5 * blue
    cr = 128 + .5 * red - .418688 * green - .081312 * blue
    skin = ((cb >= 77) & (cb <= 135) & (cr >= 133) & (cr <= 178)
            & (red > green - 5) & (red > blue)).astype(np.float32)
    y, x = np.mgrid[0:height, 0:width]
    x = (x + .5) / width
    y = (y + .5) / height
    # Portraits often have smooth faces, so texture alone is insufficient.
    head_prior = np.exp(-.5 * (((x - .5) / .22) ** 2 + ((y - .32) / .21) ** 2))
    skin_weight = .35 + 1.65 * np.clip((.78 - y) / .50, 0, 1)
    importance = .55 * texture + .45 * edge_density + skin_weight * _box_mean(skin, 3) + .6 * head_prior
    integral = _integral(importance)

    margin = max(1, round(min(width, height) * .035))
    target = min(original_width * ratio, original_height * ratio / aspect)
    sx, sy = width / original_width, height / original_height
    box_width = max(3, round(target * sx))
    box_height = max(3, round(target * aspect * sy))
    if box_width > width - 2 * margin or box_height > height - 2 * margin:
        raise ValueError('名片尺寸不足以放置奇遇图片。')
    xs = np.unique(np.append(np.arange(margin, width - margin - box_width + 1, 3), width - margin - box_width))
    ys = np.unique(np.append(np.arange(margin, height - margin - box_height + 1, 3), height - margin - box_height))
    left, top = np.meshgrid(xs, ys)
    right, bottom = left + box_width, top + box_height
    scores = (integral[bottom, right] - integral[top, right]
              - integral[bottom, left] + integral[top, left]) / (box_width * box_height)
    # Keep the selected size; on tied plain backgrounds prefer bottom-right.
    scores += .004 * (((left + box_width / 2) / width - .8) ** 2
                     + ((top + box_height / 2) / height - .8) ** 2)
    index = np.unravel_index(np.argmin(scores), scores.shape)
    score, left, top = float(scores[index]), int(left[index]), int(top[index])
    result_width = max(1, round(target))
    result_height = max(1, round(result_width * aspect))
    result_left = min(max(0, round(left / sx)), original_width - result_width)
    result_top = min(max(0, round(top / sy)), original_height - result_height)
    return Placement(result_left, result_top, result_width, result_height, score,
                     (time.perf_counter() - started) * 1000)


def composite_card(card_bytes: bytes, popup: Image.Image, *, size: str = '中') -> tuple[bytes, Placement]:
    """Decode, place and encode in the caller's background thread."""
    try:
        with Image.open(io.BytesIO(card_bytes)) as source:
            if source.width * source.height > MAX_CARD_PIXELS:
                raise ValueError('名片图片过大，请使用不超过 1600 万像素的图片。')
            card = ImageOps.exif_transpose(source).convert('RGBA')
    except (OSError, Image.DecompressionBombError) as error:
        raise ValueError('名片服务返回的内容不是有效图片。') from error
    placement = find_placement(card, popup.height / popup.width, size=size)
    # Analyse the original card, then upscale only the output canvas. Preserve
    # native popup detail instead of shrinking it and enlarging the final PNG.
    scale = max(1.0, min(
        popup.width / placement.width,
        MAX_UPSCALE,
        UPSCALE_EDGE_LIMIT / max(card.size),
        (UPSCALE_PIXEL_BUDGET / (card.width * card.height)) ** .5,
    ))
    if scale > 1.0:
        card = card.resize((round(card.width * scale), round(card.height * scale)), Image.Resampling.LANCZOS)
        width = round(placement.width * scale)
        height = round(width * popup.height / popup.width)
        placement = replace(
            placement,
            left=min(round(placement.left * scale), card.width - width),
            top=min(round(placement.top * scale), card.height - height),
            width=width,
            height=height,
            output_scale=scale,
        )
    overlay = popup if popup.size == (placement.width, placement.height) else popup.resize(
        (placement.width, placement.height), Image.Resampling.LANCZOS
    )
    card.alpha_composite(overlay, (placement.left, placement.top))
    output = io.BytesIO()
    card.save(output, format='PNG', compress_level=3)
    return output.getvalue(), placement
