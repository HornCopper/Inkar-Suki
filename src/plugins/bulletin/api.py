from src.tools.dep import *
from PIL import Image, ImageDraw, ImageFont

async def get_bulletinG(msg: str):
    background = Image.open(bot_path.PLUGINS + "/bulletin/bulletinG.jpg")
    draw = ImageDraw.Draw(background)
    width, height = background.size
    if len(msg) <= 5:
        fsize = 96
    elif 5 < len(msg) <= 10:
        fsize = 64
    elif 10 < len(msg) <= 20:
        fsize = 64
        msg = msg[:9] + "\n" + msg[9:]
    font = ImageFont.truetype(bot_path.ASSETS + "/font/syst-heavy.otf", fsize)
    bbox = draw.textbbox((0, 0), msg, font=font)  
    text_width = bbox[2] - bbox[0]  
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) / 2  
    y = (height - text_height) / 2
    draw.text((x, y), msg, font=font, align="center", fill=(255, 0, 0), outline=(255, 255, 0), stroke_fill=(255, 255, 0), stroke_width=1)
    new_file = bot_path.CACHE + "/" + get_uuid() + ".jpg"
    background.save(new_file)
    return Path(new_file).as_uri()