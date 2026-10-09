"""Compose the client-layout serendipity popup without bot dependencies."""
from pathlib import Path

from PIL import Image


def compose_serendipity_image(illustration: str | Path, assets: str | Path) -> Image.Image:
    illustration = Path(illustration)
    base = Path(assets) / 'image/jx3/serendipity'
    name = illustration.stem.split('-', 1)[0]

    def load(path: Path) -> Image.Image:
        with Image.open(path) as image:
            return image.convert('RGBA')

    background = load(base / 'vector/background.png')
    source_size = background.size
    art = load(illustration)
    icon = load(base / 'vector/icon.png')
    close = load(base / 'vector/close.png')
    name_path = base / 'name' / f'{name}.png'
    if not name_path.is_file():
        name_path = base / 'name/宠物奇缘.png'
    title = load(name_path)
    size = (500, 522)
    background = background.resize(size, Image.Resampling.LANCZOS)
    art = art.crop((0, 0, *source_size)).resize(size, Image.Resampling.LANCZOS)
    background.alpha_composite(icon, (60, 40))
    background.alpha_composite(art, (0, 0))
    background.alpha_composite(title.resize((160, 46), Image.Resampling.LANCZOS), (164, 446))
    background.alpha_composite(close.resize((36, 36), Image.Resampling.LANCZOS), (430, 50))
    return background
