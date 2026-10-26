"""Static FriendTip header, using extracted game textures and the existing FZHT font.

The client uses animated PSS/GIF resources; these exports use portrait planes /
first frames. Pillow's font rasterizer and independent panel slicing may differ.
"""
from dataclasses import dataclass
from functools import lru_cache
import io
import math

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

from src.utils.database.constant import CURRENT_LEVEL

from .catalog import BODIES, Catalog, LABELS, PAGE_SIZE, Selection
from .report import ReportStyle


@dataclass(frozen=True)
class Role:
    name: str
    server: str
    school: str
    camp: str
    body: str = ''


def png(image: Image.Image) -> bytes:
    output = io.BytesIO()
    image.save(output, format='PNG', optimize=True)
    return output.getvalue()


@lru_cache(maxsize=64)
def font(path: str, size: int):
    return ImageFont.truetype(path, size)


def ellipsis(text: str, face, width: float) -> str:
    text = ' '.join(str(text).split())
    if face.getlength(text) <= width:
        return text
    while text and face.getlength(text + '…') > width:
        text = text[:-1]
    return text + '…' if text else ''


class Renderer:
    def __init__(self, catalog: Catalog, scale: int = 4, ui_color: str = '默认'):
        self.catalog = catalog
        self.scale = scale
        self.font_file = str(catalog.assets / 'font' / catalog.data['fonts']['file'])
        self.report_style = ReportStyle(catalog.assets, ui_color)

    def scaled(self, values):
        return tuple(round(value * self.scale) for value in values)

    def image(self, reference: str):
        with Image.open(self.catalog.path(reference)) as source:
            return source.convert('RGBA')

    def resized(self, image, size):
        return image.resize(self.scaled(size), Image.Resampling.LANCZOS)

    def panel(self):
        source = self.image(self.catalog.data['common']['panel'])
        # Preserve the popup's corners and bottom placement at its original
        # 449-pixel full height, then take just the requested header.
        out = Image.new('RGBA', self.scaled((400, 449)))
        edges_x = [0, 13, source.width - 13, source.width]
        edges_y = [0, 13, source.height - 13, source.height]
        target_x, target_y = self.scaled((0, 13, 387, 400)), self.scaled((0, 13, 436, 449))
        for row in range(3):
            for column in range(3):
                tile = source.crop((edges_x[column], edges_y[row], edges_x[column + 1], edges_y[row + 1]))
                tile = tile.resize((target_x[column + 1] - target_x[column], target_y[row + 1] - target_y[row]),
                                   Image.Resampling.LANCZOS)
                out.alpha_composite(tile, (target_x[column], target_y[row]))
        return out.crop(self.scaled((0, 0, 400, 194)))

    def avatar(self, variant: dict, border: dict) -> Image.Image:
        layer = Image.new('RGBA', self.scaled((128, 136)))
        backing = self.resized(self.image(self.catalog.data['common']['backing']), (75, 75))
        backing.putalpha(backing.getchannel('A').point(lambda value: value // 2))
        layer.alpha_composite(backing, self.scaled((26, 36)))
        frame = self.resized(self.image(border['image']), (122, 122))
        layer.alpha_composite(frame.crop(self.scaled((0, 0, 122, 61))), self.scaled((3, 12)))
        portrait = self.image(variant['image'])
        if variant.get('flip'):
            portrait = ImageOps.mirror(portrait)
        handle = Image.new('RGBA', self.scaled((73, 93)))
        if variant['kind'] == 'pss':
            handle.alpha_composite(self.resized(portrait, (67.2, 75.6)), self.scaled((0, 19)))
        else:
            handle.alpha_composite(self.resized(portrait, (56, 63)), self.scaled((8, 24)))
        mask = self.image(self.catalog.data['common']['mask']).getchannel('A').resize(handle.size, Image.Resampling.LANCZOS)
        handle.putalpha(ImageChops.multiply(handle.getchannel('A'), mask))
        layer.alpha_composite(handle, self.scaled((27, 17)))
        layer.alpha_composite(frame.crop(self.scaled((0, 61, 122, 122))), self.scaled((3, 73)))
        return layer

    def text(self, canvas, text, rect, size, center=False):
        x, y, width, height = self.scaled(rect)
        face = font(self.font_file, size * self.scale)
        value = ellipsis(text, face, width)
        draw = ImageDraw.Draw(canvas)
        bounds = draw.textbbox((0, 0), value, font=face)
        if center:
            y += (height - (bounds[3] - bounds[1])) / 2
        y -= bounds[1]
        styles = self.catalog.data['fonts']
        offset = styles['shadow_offset'] * self.scale
        draw.text((x + offset, y + offset), value, font=face, fill=tuple(styles['shadow']) + (255,))
        draw.text((x, y), value, font=face, fill=tuple(styles['color']) + (255,))
        return face.getlength(value) / self.scale

    def card(self, role: Role, signature: str, background: Selection, avatar: Selection, frame: Selection) -> bytes:
        # A neutral solid scene makes translucent game textures legible in chat.
        card = Image.new('RGBA', self.scaled((400, 194)), (22, 31, 34, 255))
        card.alpha_composite(self.panel())
        card.alpha_composite(self.resized(self.image(background.entry['image']), (394, 190)), self.scaled((3, 3)))
        card.alpha_composite(self.avatar(self.catalog.variant(avatar, role.body), frame.entry))
        self.text(card, role.name, (125, 36, 258, 25), 20, True)
        school_width = self.text(card, role.school, (125, 68, 170, 16), 15, True)
        level_x = 125 + school_width + 8
        level_width = self.text(card, str(CURRENT_LEVEL), (level_x, 68, 40, 16), 15, True)
        self.text(card, '级', (level_x + level_width + 2, 68, 20, 16), 15, True)
        self.text(card, '服务器', (125, 94, 60, 24), 15)
        self.text(card, role.server, (185, 94, 198, 24), 15)
        self.text(card, '阵营', (17, 136, 45, 20), 15, True)
        self.text(card, role.camp, (62, 136, 323, 20), 15, True)
        self.text(card, signature, (17, 162, 368, 32), 14, True)
        return png(card.convert('RGB'))

    def sample(self, category: str, selection: Selection, width: int = 360) -> Image.Image:
        entry = selection.entry
        ratio = width / 360
        def px(value):
            return round(value * ratio)
        if category == 'backgrounds':
            return self.image(entry['image']).resize((width, px(174)), Image.Resampling.LANCZOS)
        if category == 'frames':
            result = Image.new('RGBA', (width, px(174)))
            image = self.image(entry['image'])
            image = ImageOps.contain(image, (px(168), px(168)), Image.Resampling.LANCZOS)
            result.alpha_composite(image, ((width - image.width) // 2, px(3)))
            return result
        bodies = [selection.body] if selection.body else list(BODIES)
        out = Image.new('RGBA', (width, px(174)))
        draw = ImageDraw.Draw(out)
        face = font(self.report_style.font_file, px(17))
        border = self.catalog.resolve('frames', '67').entry
        for index, body in enumerate(bodies):
            # Match the same mirror/mask/frame branch used by the final card.
            image = self.avatar(entry['variants'][body], border)
            size = px(132 if len(bodies) == 1 else 87)
            image = image.resize((size, round(size * 136 / 128)), Image.Resampling.LANCZOS)
            x = (width - size) // 2 if len(bodies) == 1 else px(index * 90 + 1)
            out.alpha_composite(image, (x, px(4)))
            text = BODIES[body]
            width = face.getlength(text)
            draw.text((x + (size - width) / 2, px(146 if len(bodies) == 1 else 103)), text, font=face,
                      fill=self.report_style.colors['secondary-text'])
        return out

    def gallery(self, category: str, entries: list[dict], page: int, keyword: str = '', body: str | None = None) -> bytes:
        pages = max(1, math.ceil(len(entries) / PAGE_SIZE))
        if page < 1 or page > pages:
            raise ValueError(f'页码超出范围，当前结果共有 {pages} 页。')
        items = entries[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]
        rows = math.ceil(len(items) / 3)
        style = self.report_style
        footer_top = 124 + rows * 246 + max(0, rows - 1) * 12 + 20
        image = Image.new('RGBA', (1152, footer_top + 92), style.colors['background'])
        draw = ImageDraw.Draw(image)
        heading = font(style.bold_file, 30)
        face, small = font(style.font_file, 22), font(style.font_file, 18)
        label = LABELS[category]
        summary = f'第 {page}/{pages} 页 · 共 {len(entries)} 项'
        if keyword:
            summary += ' · 搜索：' + keyword
        if body:
            summary += ' · ' + BODIES[body]
        style.header(image, f'社交名片 · {label}图鉴', ellipsis(summary, small, 1100), heading, small)
        for index, entry in enumerate(items):
            x, y = (index % 3) * 388, 124 + (index // 3) * 258
            draw.rounded_rectangle((x, y, x + 375, y + 245), radius=4,
                                   fill=style.colors['muted-surface'], outline=style.colors['border'])
            image.alpha_composite(self.sample(category, Selection(entry, body)), (x + 8, y + 8))
            title = f'{entry["id"]}  {entry["name"]}'
            draw.text((x + 12, y + 190), ellipsis(title, face, 350), font=face, fill=style.colors['text'], anchor='lt')
            subtitle = '体型根据角色详情自动选择' if category == 'avatars' else '生成时填写编号或名称'
            draw.text((x + 12, y + 222), subtitle, font=small, fill=style.colors['secondary-text'], anchor='lt')
        style.footer(image, footer_top,
                     f'社交名片 {label} [页码] [关键词]  |  社交名片 预览 {label} 编号', small, small)
        return png(style.finish(image))

    def preview(self, category: str, selection: Selection) -> bytes:
        # A larger isolated material, accompanied by its exact selectable ID.
        sample = self.sample(category, selection, width=1080)
        style = self.report_style
        image = Image.new('RGBA', (1152, 858), style.colors['background'])
        face, small = font(style.bold_file, 30), font(style.font_file, 18)
        title = f'{selection.entry["id"]}  {selection.entry["name"]}'
        style.header(image, f'社交名片 · {LABELS[category]}预览', ellipsis(title, small, 1100), face, small)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((0, 124, 1151, 686), radius=4,
                               fill=style.colors['muted-surface'], outline=style.colors['border'])
        image.alpha_composite(sample, (36, 144))
        note = '萝莉 / 成女 / 正太 / 成男；生成时自动匹配角色体型' if category == 'avatars' else '生成名片时可直接填此编号或名称'
        draw.text((576, 710), note, font=font(style.font_file, 22), fill=style.colors['secondary-text'], anchor='mt')
        style.footer(image, 766, f'可填：{selection.entry["id"]} 或 {selection.entry["name"]}', small, small)
        return png(style.finish(image))
