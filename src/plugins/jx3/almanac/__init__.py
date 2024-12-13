from pathlib import Path
from collections import Counter

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Message,
    GroupMessageEvent,
    MessageSegment as ms
)
from nonebot.params import CommandArg

from src.config import Config
from src.const.path import CONST
from src.utils.time import Time
from src.utils.network import Request
from src.utils.generate import generate

import os
import re
import httpx

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

AlmanacMatcher = on_command("jx3_almanac", aliases={"剑三黄历"}, priority=5)

@AlmanacMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    today = Time().format("%Y-%m-%d")
    if not os.path.exists(CONST + "/cache/" + today + ".jpg"):
        await AlmanacMatcher.finish("今日剑三黄历尚未更新，请稍后再查询！\n（还没更新？快去敲音卡作者起床！")
    else:
        image = ms.image(
            Request(
                Path(
                    CONST + "/cache/" + today + ".jpg"
                ).as_uri()
            ).local_content
        )
        words = extract_chinese(args.extract_plain_text())
        if not words:
            await AlmanacMatcher.finish("未检测到中文字符！")
        else:
            async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
                words_attr_data = (await client.post("https://inkar-suki.codethink.cn/words_attr", params={"token": Config.hidden.offcial_token,"words": words})).json()
            if words_attr_data["code"] != 200:
                await AlmanacMatcher.finish("分析五行失败，请检查角色名，确认无误的话请联系音卡作者！")
            else:
                words_attr: list[str] = words_attr_data["data"]
                ref_attr = most_common_element(words_attr)
                msg = f"{words} 对应五行：\n" + "|".join(words_attr) + f"\n参考属性：{ref_attr}\n" + image + "数据来自小红书【剑三黄历】欢迎关注！"
                await AlmanacMatcher.finish(msg)

AlmanacImageMatcher = on_command("jx3_almanac_image", aliases={"黄历图片生成"}, priority=5)

@AlmanacImageMatcher.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    full_msg = msg.extract_plain_text().strip().replace("\r", "\n")
    try:
        html: str = get_almanac_image(full_msg)
    except:
        await AlmanacImageMatcher.finish("解析失败！")
    image = await generate(html, ".container", segment=True)
    await AlmanacImageMatcher.finish(image)