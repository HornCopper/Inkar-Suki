"""Fixed-size notifications using extracted JX3 artwork and stamp frames."""
from functools import lru_cache
import io
from pathlib import Path
import warnings

from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

from .options import TipRequest


ASSETS = Path(__file__).resolve().parents[3] / 'assets'
IMAGE_PATH = ASSETS / 'image/jx3/achievement_tip'
FONT_PATH = ASSETS / 'font/fzht.ttf'
SCALE = 2
SIZE = (806, 276)
HOLD_MS = 1700
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_ICON_PIXELS = 16_000_000


@lru_cache(maxsize=32)
def asset(name: str, size: tuple[int, int] | None = None) -> Image.Image:
    with Image.open(IMAGE_PATH / name) as image:
        result = image.convert('RGBA')
    size = size or (result.width * SCALE, result.height * SCALE)
    return result.resize(size, Image.Resampling.LANCZOS)


@lru_cache(maxsize=24)
def font(size: int):
    return ImageFont.truetype(str(FONT_PATH), size * SCALE)


def custom_icon(content: bytes) -> Image.Image:
    if len(content) > MAX_IMAGE_BYTES:
        raise ValueError('图标图片不能超过 8 MiB，请缩小后重新发送。')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(content)) as image:
                if image.width * image.height > MAX_ICON_PIXELS:
                    raise ValueError('图标图片不能超过 1600 万像素，请缩小后重新发送。')
                # Animated uploads use their first frame as the stationary icon.
                image.seek(0)
                oriented = ImageOps.exif_transpose(image).convert('RGBA')
                return ImageOps.fit(oriented, (96, 96), Image.Resampling.LANCZOS,
                                    centering=(0.5, 0.5))
    except (UnidentifiedImageError, OSError, SyntaxError):
        raise ValueError('无法读取图标图片，请重新发送 PNG、JPG、WebP 或 GIF 原图。') from None
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise ValueError('图标图片像素过大，请缩小后重新发送。') from None


def _layer(canvas, name, xy, size=None):
    canvas.alpha_composite(asset(name, size), (xy[0] * SCALE, xy[1] * SCALE))


def _text(canvas, value, box, font_size, align='left'):
    if not value:
        return
    x, y, width, height = (part * SCALE for part in box)
    face = font(font_size)
    if face.getlength(value) > width:
        while value and face.getlength(value + '...') > width:
            value = value[:-1]
        value += '...'
    tile = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(tile)
    bounds = draw.textbbox((0, 0), value, font=face)
    left = 0
    if align == 'center':
        left = (width - face.getlength(value)) / 2
    elif align == 'right':
        left = width - face.getlength(value)
    top = (height - (bounds[3] - bounds[1])) / 2 - bounds[1]
    draw.text((round(left), round(top)), value, font=face, fill=(0, 0, 0, 255))
    canvas.alpha_composite(tile, (x, y))


def base_image(request: TipRequest, icon: Image.Image | None = None) -> Image.Image:
    canvas = Image.new('RGBA', SIZE)
    _layer(canvas, 'background.png', (0, 0))
    _layer(canvas, 'description_bg.png', (45, 90), (670, 60))
    canvas.alpha_composite(icon if icon is not None else asset('default_icon.png'), (112, 86))
    points = str(request.points)
    # Use the free space before the right-aligned score, with a six-pixel gap.
    point_width = min(font(20).getlength(points), 50 * SCALE)
    title_width = int(348 - 126 - 6 - point_width / SCALE)
    _text(canvas, request.title, (126, 49, title_width, 30), 16)
    _text(canvas, request.description, (70, 98, 275, 20), 15, 'center')
    _text(canvas, points, (298, 46, 50, 30), 20, 'right')
    _layer(canvas, 'points.png', (350, 43))
    _layer(canvas, 'name_separator.png', (114, 57))
    _text(canvas, '隐元秘鉴', (179, 15, 275, 20), 16)
    _layer(canvas, 'close.png', (375, 15), (40, 40))
    return canvas


def stamped(base: Image.Image, index: int = 6) -> Image.Image:
    image = base.copy()
    _layer(image, f'finish_{index}.png', (156, 0))
    return image


def animation(base: Image.Image):
    frames = [base] + [stamped(base, index) for index in range(7)]
    durations = [500] + [100] * 7
    durations[-1] += HOLD_MS
    frames.append(Image.new('RGBA', SIZE))
    durations.append(100)
    return frames, durations


def render(request: TipRequest, icon: Image.Image | None = None) -> bytes:
    base = base_image(request, icon)
    output = io.BytesIO()
    if request.format == 'png':
        stamped(base).save(output, format='PNG')
        return output.getvalue()
    frames, durations = animation(base)
    if request.format == 'apng':
        frames[0].save(output, format='PNG', save_all=True, append_images=frames[1:],
                       duration=durations, loop=1, disposal=0, blend=0, default_image=False)
    else:
        # Loop directly from the completed stamp to the initial panel.
        # Move the closing frame's time onto the final stamp to keep 3 seconds.
        closing_duration = durations[-1]
        frames, durations = frames[:-1], durations[:-1]
        durations[-1] += closing_duration
        # Share the palette so the stationary paper and text do not change
        # color between frames; reserve entry 255 for binary transparency.
        sample = Image.new('RGB', (SIZE[0], SIZE[1] * len(frames)))
        for index, frame in enumerate(frames):
            sample.paste(frame.convert('RGB'), (0, index * SIZE[1]))
        palette = sample.quantize(colors=255, method=Image.Quantize.FASTOCTREE)
        converted = []
        for frame in frames:
            indexed = frame.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE)
            indexed.paste(255, mask=frame.getchannel('A').point(lambda v: 255 if v < 128 else 0))
            indexed.info['transparency'] = 255
            converted.append(indexed)
        converted[0].save(output, format='GIF', save_all=True, append_images=converted[1:],
                          duration=durations, loop=0, disposal=2, transparency=255,
                          background=255, optimize=False)
    return output.getvalue()
