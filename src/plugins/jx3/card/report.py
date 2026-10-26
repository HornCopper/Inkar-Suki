"""Use the project's shared report palette, frame and font for material browsing."""
from functools import lru_cache
import re

from PIL import ImageDraw

from src.utils.image_style import frame_report
from src.utils.ui_theme import build_ui_color_css


def variables(css: str) -> dict[str, str]:
    return dict(re.findall(r'--inkar-([a-z-]+):\s*(#[0-9a-fA-F]{6})\s*;', css))


@lru_cache(maxsize=2)
def default_palette(path: str) -> dict[str, str]:
    from pathlib import Path
    return variables(Path(path).read_text(encoding='utf-8').split('}', 1)[0])


class ReportStyle:
    def __init__(self, assets, ui_color='默认'):
        self.colors = dict(default_palette(str(assets.parent / 'templates/style_2.css')))
        custom = build_ui_color_css(ui_color)
        self.colors.update(variables(custom))
        self.title = self.colors['accent-ink'] if custom else self.colors['text']
        self.custom = bool(custom)
        self.font_file = str(assets / 'font/PingFangSC-Medium.otf')
        self.bold_file = str(assets / 'font/PingFangSC-Semibold.otf')

    def header(self, canvas, title, subtitle, face, small):
        draw = ImageDraw.Draw(canvas)
        draw.rounded_rectangle((0, 0, canvas.width - 1, 103), radius=4,
                               fill=self.colors['muted-surface'], outline=self.colors['border'])
        if self.custom:
            draw.rectangle((0, 2, 3, 101), fill=self.colors['accent'])
        draw.text((24, 20), title, font=face, fill=self.title, anchor='lt')
        draw.text((24, 65), subtitle, font=small, fill=self.colors['secondary-text'], anchor='lt')

    @staticmethod
    def footer(canvas, top, instruction, face, small):
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, top, canvas.width, canvas.height), fill='#f0f0f0')
        draw.text((canvas.width / 2, top + 17), instruction, font=face, fill='#777777', anchor='mt')
        draw.text((canvas.width / 2, top + 55), 'Inkar Suki · 社交名片素材', font=small, fill='#777777', anchor='mt')

    @staticmethod
    def finish(canvas):
        return frame_report(canvas, padding=24).convert('RGB')
