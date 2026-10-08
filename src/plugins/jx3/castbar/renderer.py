"""Castbar rendering extracted from the local workshop; no HTTP server or game dependency."""
from functools import lru_cache
import io
import json
import math
from pathlib import Path
import threading

from PIL import Image, ImageChops, ImageDraw

from src.const.path import ASSETS, build_path

from .cache import ByteCache
from .fonts import enumerate_fonts, text_runs

IMAGE_PATH = Path(build_path(ASSETS, ['image', 'jx3', 'castbar']))
SOURCE_PATH = Path(build_path(ASSETS, ['source', 'jx3', 'castbar']))
STYLES = json.loads((SOURCE_PATH / 'styles.json').read_text(encoding='utf-8'))
BY_ID = {s['id']: s for s in STYLES}
EXPORT_LOCK = threading.Lock()
RESIZED_ASSETS = ByteCache(max_bytes=32 * 1024 * 1024, max_entries=512)
GAME_FONT_PATH = Path(build_path(ASSETS, ['font', 'fzht.ttf']))
DEFAULT_FONT_SIZE = 15  # FontScheme 18 -> FontID 1 -> fontlist.ini Size=15.


def available_fonts():
    fonts = enumerate_fonts([GAME_FONT_PATH], include_system=False)
    for font in fonts:
        if Path(font['path']) == GAME_FONT_PATH:
            font['label'] += ' · 游戏默认'
    return fonts


LOCAL_FONTS = available_fonts()
FONTS_BY_ID = {font['id']: font for font in LOCAL_FONTS}
DEFAULT_FONT = next(font for font in LOCAL_FONTS if Path(font['path']) == GAME_FONT_PATH)
FALLBACK_FONT = next((font for font in LOCAL_FONTS if Path(font['path']).name.casefold() == 'msyh.ttc' and font['index'] == 0), DEFAULT_FONT)


def settings(data):
    school = str(data.get('school', 'changge'))
    if school not in BY_ID:
        raise ValueError('请选择列表中的职业。')
    duration = float(data.get('duration', 2.12))
    fps = int(data.get('fps', 20))
    scale = int(data.get('scale', 2))
    strength = float(data.get('strength', 1))
    elapsed = float(data.get('elapsed', min(0.71, duration)))
    segments = int(data.get('segments', 4))
    font_id = str(data.get('fontId', DEFAULT_FONT['id']))
    font_size = float(data.get('fontSize', DEFAULT_FONT_SIZE))
    if not math.isfinite(duration) or not 0.1 <= duration <= 30:
        raise ValueError('总时长须在 0.1 至 30 秒之间。')
    if fps not in [10, 20, 30] or (not any(key in data for key in ['width', 'height']) and scale not in [1, 2, 3]):
        raise ValueError('帧率或尺寸无效。')
    scene = BY_ID[school]
    if ('width' in data) != ('height' in data):
        raise ValueError('请同时设置宽度和高度。')
    output_width = float(data.get('width', scene['width']*scale))
    output_height = float(data.get('height', scene['height']*scale))
    if not math.isfinite(output_width) or not output_width.is_integer() or not 16 <= output_width <= 4096:
        raise ValueError('宽度须为 16 至 4096 像素的整数。')
    if not math.isfinite(output_height) or not output_height.is_integer() or not 16 <= output_height <= 2048:
        raise ValueError('高度须为 16 至 2048 像素的整数。')
    output_width, output_height = int(output_width), int(output_height)
    scale = min(8, max(1, math.ceil(max(output_width/scene['width'], output_height/scene['height']))))
    if not math.isfinite(strength) or not 0 <= strength <= 2:
        raise ValueError('光效强度须在 0 至 2 之间。')
    if not math.isfinite(elapsed) or not 0 <= elapsed <= duration:
        raise ValueError('当前时间须在 0 和读条总时间之间。')
    if not 1 <= segments <= 30:
        raise ValueError('小节数量须在 1 至 30 之间。')
    if font_id not in FONTS_BY_ID:
        raise ValueError('所选本机字体不可用，请刷新字体列表后重选。')
    if not math.isfinite(font_size) or not font_size.is_integer() or not 8 <= font_size <= 36:
        raise ValueError('字号须为 8 至 36 的整数。')
    export_end = data.get('exportEnd', 'full')
    if export_end not in ['full', 'current']:
        raise ValueError('动画导出范围无效。')
    if data.get('direction', 'forward') not in ['forward', 'reverse']:
        raise ValueError('读条方向无效。')
    background = data.get('background', 'transparent')
    if background not in ['transparent', 'dark', 'light']:
        raise ValueError('背景无效。')
    return dict(school=school, duration=duration, fps=fps, scale=scale, width=output_width, height=output_height, strength=strength,
                direction=data.get('direction', 'forward'), background=background,
                skill=str(data.get('skill', BY_ID[school]['skill']))[:40],
                showTime=bool(data.get('showTime', True)), particles=bool(data.get('particles', True)),
                elapsed=elapsed, segments=segments, showSegments=bool(data.get('showSegments', True)),
                exportEnd=export_end, fontId=font_id, fontSize=int(font_size),
                fontName=FONTS_BY_ID[font_id]['label'])


@lru_cache(maxsize=600)
def asset(path):
    return Image.open(IMAGE_PATH / path).convert('RGBA')


def resized_asset(path, size):
    # Cached sprites are shared: callers must copy before changing pixels.
    key = (path, size)
    sprite = RESIZED_ASSETS.get(key)
    if sprite is None:
        sprite = asset(path).resize(size, Image.Resampling.LANCZOS)
        RESIZED_ASSETS.put(key, sprite, sprite.width * sprite.height * 4)
    return sprite


def particle_asset(path, size):
    key = ('particle', path, size)
    sprite = RESIZED_ASSETS.get(key)
    if sprite is None:
        sprite = resized_asset(path, size).copy()
        r, g, b, alpha = sprite.split()
        light = ImageChops.lighter(ImageChops.lighter(r, g), b)
        sprite.putalpha(ImageChops.multiply(alpha, light))
        RESIZED_ASSETS.put(key, sprite, sprite.width * sprite.height * 4)
    return sprite


def particle_sources(style):
    sprites = [t for t in style['particleTextures'] if any(k in t['source'] for k in ['光点', '羽毛', '樱花', '火星', '叶子'])]
    return sprites[:5] or style['particleTextures'][:3]


def particles(style, elapsed, strength):
    bar = next(l for l in style['layers'] if l['progress'])
    sources = particle_sources(style)
    count = round(14 * strength)
    for i in range(count):
        phase = (elapsed * (0.24 + (i % 4) * 0.025) + i * 0.61803398875) % 1
        fade = math.sin(math.pi * phase) ** 1.3 * 0.65
        x = bar['x'] - 10 + phase * (bar['width'] + 20)
        y = bar['y'] + bar['height'] / 2 + math.sin(phase * math.pi * 2 + i * 1.7) * (7 + i % 3 * 3)
        size = 7 + i % 4 * 3
        angle = math.sin(elapsed * 0.8 + i) * 0.6
        yield dict(src=sources[i % len(sources)]['src'] if sources else None,
                   x=x, y=y, size=size, angle=angle, alpha=fade)


def render(data, elapsed):
    image = render_native(data, elapsed)
    size = (data['width'], data['height'])
    return image if image.size == size else image.resize(size, Image.Resampling.LANCZOS)


def render_native(data, elapsed):
    style = BY_ID[data['school']]
    scale = data['scale']
    elapsed = max(0, min(float(elapsed), data['duration']))
    fraction = elapsed / data['duration']
    fill = 1-fraction if data['direction'] == 'reverse' else fraction
    bg = {'transparent': (0, 0, 0, 0), 'dark': (24, 38, 56, 255), 'light': (232, 240, 246, 255)}[data['background']]
    image = Image.new('RGBA', (style['width']*scale, style['height']*scale), bg)
    for layer in style['layers']:
        sprite = resized_asset(layer['src'], (layer['width']*scale, layer['height']*scale))
        if layer['progress']:
            # Crop the full texture; do not squeeze it into a shrinking width.
            width = round(sprite.width * fill)
            if not width:
                continue
            sprite = sprite.crop((0, 0, width, sprite.height))
        image.alpha_composite(sprite, (layer['x']*scale, layer['y']*scale))
    if data['particles'] and data['strength']:
        head = style.get('headGlow')
        if head:
            pulse = (0.18 + 0.08*math.sin(elapsed*4.8)) * min(2, data['strength'])
            marks = [(head['x'], head['y'], head['size'], pulse)]
            for i, (dx, dy) in enumerate(head['points']):
                phase = 0.5 + 0.5*math.sin(elapsed*(3.9+i*0.7)+i*2.1)
                marks.append((head['x']+dx, head['y']+dy, 18+phase*12, (0.2+phase*0.6)*min(2, data['strength'])))
            for x, y, size, opacity in marks:
                sprite = resized_asset(head['src'], (max(1, round(size*scale)), max(1, round(size*scale)))).copy()
                sprite.putalpha(sprite.getchannel('A').point(lambda a: round(a*min(1, opacity))))
                image.alpha_composite(sprite, (round(x*scale-sprite.width/2), round(y*scale-sprite.height/2)))
        for part in particles(style, elapsed, data['strength']):
            size = max(1, round(part['size']*scale))
            if part['src']:
                sprite = particle_asset(part['src'], (size, size)).copy()
            else:
                sprite = Image.new('RGBA', (size, size))
                ImageDraw.Draw(sprite).ellipse((size/3, size/3, size*2/3, size*2/3), fill=(145, 225, 250, 255))
                r, g, b, alpha = sprite.split()
                light = ImageChops.lighter(ImageChops.lighter(r, g), b)
                sprite.putalpha(ImageChops.multiply(alpha, light))
            # Original particle materials often use additive blending on black.
            alpha = sprite.getchannel('A').point(lambda v: round(v*part['alpha']))
            sprite.putalpha(alpha)
            sprite = sprite.rotate(-math.degrees(part['angle']), Image.Resampling.BICUBIC, expand=True)
            image.alpha_composite(sprite, (round(part['x']*scale-sprite.width/2), round(part['y']*scale-sprite.height/2)))
    if data['direction'] == 'reverse' and data['showSegments']:
        bar = next(l for l in style['layers'] if l['progress'])
        line = style['segment']['line']
        sprite = resized_asset(line['src'], (line['width']*scale, line['height']*scale))
        for i in range(1, data['segments']):
            x = bar['x'] + bar['width'] * i / data['segments']
            y = bar['y'] + bar['height']/2
            image.alpha_composite(sprite, (round(x*scale-sprite.width/2), round(y*scale-sprite.height/2)))
            delta = elapsed - data['duration'] * (data['segments']-i) / data['segments']
            shine = style['segment'].get('shine')
            if shine and 0 <= delta < 0.18:
                flare = resized_asset(shine['src'], (shine['width']*scale, shine['height']*scale)).copy()
                flare.putalpha(flare.getchannel('A').point(lambda a: round(a*(1-delta/0.18))))
                image.alpha_composite(flare, (round(x*scale-flare.width/2), round(y*scale-flare.height/2)))
    text = style['text']
    label = data['skill']
    if data['showTime']:
        label += f' ({elapsed:.2f}/{data["duration"]:.2f})'
    draw = ImageDraw.Draw(image)
    center = ((text['x']+text['width']/2)*scale, (text['y']+text['height']/2)*scale)
    runs = text_runs(label, FONTS_BY_ID[data['fontId']], FALLBACK_FONT, data['fontSize']*scale)
    widths = [draw.textlength(run, font=font) for run, font in runs]
    x = center[0] - sum(widths)/2
    for (run, font), width in zip(runs, widths):
        draw.text((x, center[1]), run, fill='white', font=font, anchor='lm', stroke_width=scale, stroke_fill=(10, 18, 28))
        x += width
    return image


def animation_plan(data, tick_ms):
    end = data['elapsed'] if data['exportEnd'] == 'current' else data['duration']
    if end < 0.01:
        raise ValueError('导出动画时，当前时间须至少为 0.01 秒。')
    if round(end * data['fps']) > 600:
        raise ValueError('动画最多 600 帧；请降低帧率或缩短时长。')
    ticks = max(1, round(end*1000/tick_ms))
    count = max(1, min(ticks, 600, round(end * data['fps']) + 1))
    if data['width']*data['height']*count > 64_000_000:
        raise ValueError('当前尺寸和动画长度过大，请减小宽高、时长或帧率。')
    durations = [tick_ms*(round((i+1)*ticks/count)-round(i*ticks/count)) for i in range(count)]
    times = [end*i/(count-1) if count > 1 else end for i in range(count)]
    return times, durations


def gif_bytes(data):
    times, durations = animation_plan(data, 10)
    frames = []
    for elapsed in times:
        rgba = render(data, elapsed)
        rgb = rgba.convert('RGB')
        # Palette generation dominates GIF export; octree keeps all frames and
        # output pixels while avoiding a median-cut pass for every frame.
        frame = rgb.quantize(colors=255, method=Image.Quantize.FASTOCTREE)
        # Use a dedicated transparent palette entry. GIF supports binary alpha.
        alpha = rgba.getchannel('A').point(lambda v: 255 if v < 96 else 0)
        frame.paste(255, mask=alpha)
        frame.info['transparency'] = 255
        frames.append(frame)
    result = io.BytesIO()
    frames[0].save(result, format='GIF', save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, disposal=2, transparency=255, optimize=False)
    return result.getvalue()


def apng_bytes(data):
    times, durations = animation_plan(data, 1)
    frames = [render(data, elapsed) for elapsed in times]
    result = io.BytesIO()
    frames[0].save(result, format='PNG', save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, disposal=0, blend=0, default_image=False)
    return result.getvalue()


