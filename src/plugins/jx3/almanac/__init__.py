from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

from nonebot.adapters.onebot.v11 import (
    Message,
    GroupMessageEvent,
    MessageSegment as ms
)
from nonebot.params import CommandArg

from src.const.path import CONST
from src.utils.command import on_command
from src.utils.time import Time
from src.utils.network import Request
from src.utils.generate import generate

import os
import re

from .image import x as get_almanac_image

def extract_chinese(text):
    chinese_chars = re.findall(r'[\u4e00-\u9fa5]+', text)
    return ''.join(chinese_chars)

def most_common_element(elements: list[str]) -> str:
    counter = Counter(elements)
    most_common = counter.most_common(1)
    if most_common:
        if sum(1 for count in counter.values() if count == most_common[0][1]) > 1:
            return "通用"
        else:
            return most_common[0][0]
    else:
        return "通用"

almanac_matcher = on_command("jx3_almanac", command_key="剑三黄历", aliases={"剑三黄历"}, priority=5)

@almanac_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    today = Time().format("%Y-%m-%d")
    if not os.path.exists(CONST + "/cache/" + today + ".png"):
        await almanac_matcher.finish("今日剑三黄历尚未更新，请稍后再查询！\n（还没更新？快去敲音卡作者起床！")
    else:
        image = ms.image(
            Request(
                Path(
                    CONST + "/cache/" + today + ".png"
                ).as_uri()
            ).local_content
        )
        msg = image + "数据来自小红书【剑三黄历】欢迎关注！"
        await almanac_matcher.finish(msg)

almanac_image_matcher = on_command("jx3_almanac_image", command_key=None, aliases={"黄历图片生成"}, priority=5)

@almanac_image_matcher.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    full_msg = msg.extract_plain_text().strip().replace("\r", "\n")
    html: str = get_almanac_image(full_msg)
    image = await generate(html, ".container", segment=True, output_path=CONST + "/cache/" + (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d") + ".png")
    await almanac_image_matcher.finish(image)
