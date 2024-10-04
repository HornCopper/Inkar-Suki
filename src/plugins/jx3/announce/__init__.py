from pathlib import Path

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.config import Config
from src.const.path import ASSETS, build_path
from src.utils.network import Request
from src.utils.generate import generate

import os
import re


AnnounceMatcher = on_command("jx3_announce", aliases={"维护公告", "更新公告", "公告", "更新"}, force_whitespace=True, priority=5)

@AnnounceMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取维护公告的图片：

    Example：-维护公告
    """
    if args.extract_plain_text() != "":
        return
    if os.path.exists(build_path(ASSETS, ["image", "jx3", "update.png"])):
        img = Request(Path(build_path(ASSETS, ["image", "jx3", "update.png"])).as_uri()).local_content
        await AnnounceMatcher.finish(ms.image(img))
    else:
        data = (await Request(f"{Config.jx3.api.url}/data/news/allnews").get()).json()
        for news in data["data"]:
            title = news["title"]
            url = news["url"]
            if re.match(r'(\d+)月(\d+)日(.*?)版本更新公告', title):
                store_path = await generate(
                    url, 
                    ".allnews_list_container", 
                    viewport={"height": 3840, "width": 2000}, 
                    hide_classes=["detail_bot", "bdshare-slide-button"], 
                    device_scale_factor=2.0,
                    output_path=build_path(ASSETS, ["image", "jx3", "update.png"])
                )
                if not isinstance(store_path, str):
                    return
                img = Request(Path(store_path).as_uri()).local_content
                await AnnounceMatcher.finish(ms.image(img))