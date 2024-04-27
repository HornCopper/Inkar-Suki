from PIL import Image, ImageDraw, ImageFont

from src.tools.basic import *

async def get_bulletinG(msg: str, type_: str):
    if type_ not in ["S", "G"]:
        return False
    background = Image.open(PLUGINS + f"/bulletin/bulletin{type_}.jpg")
    draw = ImageDraw.Draw(background)
    width, height = background.size
    if len(msg) <= 5:
        fsize = 96
    elif 5 < len(msg) <= 10:
        fsize = 64
    elif 10 < len(msg) <= 20:
        fsize = 64
        msg = msg[:9] + "\n" + msg[9:]
    font = ImageFont.truetype(ASSETS + "/font/syst-heavy.otf", fsize)
    bbox = draw.textbbox((0, 0), msg, font=font)  
    text_width = bbox[2] - bbox[0]  
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) / 2  
    y = (height - text_height) / 2
    if type_ == "G":
        f = (255, 0, 0) # fill color
        o = (255, 255, 0) # outline color
    else:
        f = (0, 0, 0)
        o = (255, 255, 255)
    draw.text((x, y), msg, font=font, align="center", fill=f, outline=o, stroke_fill=o, stroke_width=1)
    new_file = CACHE + "/" + get_uuid() + ".jpg"
    background.save(new_file)
    return Path(new_file).as_uri()