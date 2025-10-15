from pathlib import Path
from typing import Literal
from PIL import Image

from nonebot.adapters.onebot.v11 import MessageSegment as ms

from src.const.path import ASSETS, CACHE, build_path
from src.plugins.jx3.joy.random_item import get_random
from src.utils.generate import get_uuid
from src.utils.network import Request

import os
import random

serendipity_percent = 20
firework_percent = 10

def get_serendipity(school: str | Literal[False]) -> str | None:
    pool = []
    if get_random(serendipity_percent):
        num = random.randint(1, 100)
        if 1 <= num <= 5:
            # 绝世
            for each_serendipity in os.listdir(ASSETS + "/image/jx3/serendipity/show/peerless"):
                serendipity_name = each_serendipity[:-4]
                if "-" in serendipity_name:
                    _, _school = serendipity_name.split("-")
                    if school == _school:
                        pool.append(ASSETS + "/image/jx3/serendipity/show/peerless/" + each_serendipity)
                else:
                    pool.append(ASSETS + "/image/jx3/serendipity/show/peerless/" + each_serendipity)
        elif 6 <= num <= 30:
            # 普通
            for each_serendipity in os.listdir(ASSETS + "/image/jx3/serendipity/show/common"):
                serendipity_name = each_serendipity[:-4]
                pool.append(ASSETS + "/image/jx3/serendipity/show/common/" + each_serendipity)
        else:
            # 宠物
            for each_serendipity in os.listdir(ASSETS + "/image/jx3/serendipity/show/pet"):
                serendipity_name = each_serendipity[:-4]
                pool.append(ASSETS + "/image/jx3/serendipity/show/pet/" + each_serendipity)
        return random.choice(pool)
    elif get_random(firework_percent):
        return ASSETS + "/image/jx3/fireworks/" + random.choice(
            os.listdir(ASSETS + "/image/jx3/fireworks/")
        )

def get_serendipity_image(serendipity_path: str) -> ms:
    if serendipity_path.split("/")[-2] == "fireworks":
        return ms.image(Request(Path(serendipity_path).as_uri()).local_content)
    serendipity_file_name = serendipity_path.split("/")[-1][:-4]
    if "-" in serendipity_file_name:
        serendipity_name, _ = serendipity_file_name.split("-")
    else:
        serendipity_name = serendipity_file_name
    
    background: Image.Image = Image.open(ASSETS + "/image/jx3/serendipity/vector/background.png")
    serendipity_show = Image.open(serendipity_path)
    icon = Image.open(ASSETS + "/image/jx3/serendipity/vector/icon.png")
    name_path = ASSETS + f"/image/jx3/serendipity/name/{serendipity_name}.png"
    if not os.path.exists(name_path):
        name_path = ASSETS + f"/image/jx3/serendipity/name/宠物奇缘.png"
    name = Image.open(name_path)

    background.alpha_composite(serendipity_show, (0, 0))
    background.alpha_composite(icon, (40, 48))
    background.alpha_composite(name, (145, 420))

    final_path = build_path(CACHE, [get_uuid() + ".png"])
    background.save(final_path)
    return ms.image(Request(Path(final_path).as_uri()).local_content)