"""Shared light frame for images drawn directly with Pillow."""

from PIL import Image, ImageDraw


def frame_report(image: Image.Image, padding: int = 20) -> Image.Image:
    """Put a generated image on the same white, subtly bordered surface as HTML reports."""
    source = image.convert("RGBA")
    canvas = Image.new(
        "RGBA",
        (source.width + padding * 2, source.height + padding * 2),
        "#ffffff",
    )
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (padding // 2, padding // 2, canvas.width - padding // 2 - 1, canvas.height - padding // 2 - 1),
        radius=4,
        fill="#ffffff",
        outline="#e7ebef",
        width=1,
    )
    canvas.alpha_composite(source, (padding, padding))
    return canvas
