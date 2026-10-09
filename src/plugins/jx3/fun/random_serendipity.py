from pathlib import Path
from typing import Literal
from src.utils.serendipity_image import compose_serendipity_image

from nonebot.adapters.onebot.v11 import MessageSegment as ms

from src.const.path import ASSETS, CACHE, CONST, build_path
from src.plugins.jx3.fun.random_item import get_random
from src.utils.generate import get_uuid
from src.utils.network import Request

import os
import random

serendipity_percent = 40
firework_percent = 10

def get_serendipity(school: str | Literal[False]) -> str | None:
    pool = []
    if get_random(serendipity_percent):
        num = random.randint(1, 100)
        if 1 <= num <= 15:
            # 绝世
            for each_serendipity in os.listdir(ASSETS + "/image/jx3/serendipity/show/peerless"):
                serendipity_name = each_serendipity[:-4]
                if "-" in serendipity_name:
                    _, _school = serendipity_name.split("-")
                    if school == _school:
                        pool.append(ASSETS + "/image/jx3/serendipity/show/peerless/" + each_serendipity)
                else:
                    pool.append(ASSETS + "/image/jx3/serendipity/show/peerless/" + each_serendipity)
        elif 15 <= num <= 55:
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
    cache_path = CONST + "/cache/serendipity/" + serendipity_file_name + "_client_ini_v1.png"
    if os.path.exists(cache_path):
        return ms.image(Request(Path(cache_path).as_uri()).local_content)
    background = compose_serendipity_image(serendipity_path, ASSETS)

    final_path = build_path(CACHE, [get_uuid() + ".png"])
    background.save(final_path)
    with open(final_path, "rb") as a:
        image = a.read()
    Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "wb") as b:
        b.write(image)
    return ms.image(Request(Path(final_path).as_uri()).local_content)
