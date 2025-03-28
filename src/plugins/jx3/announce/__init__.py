from pathlib import Path

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Message,
    GroupMessageEvent,
    MessageSegment as ms
)
from nonebot.params import CommandArg

from src.const.path import ASSETS, build_path
from src.utils.network import Request

import os

from .image import get_image

AnnounceMatcher = on_command("jx3_announce", aliases={"维护公告", "更新公告", "公告", "更新"}, force_whitespace=True, priority=5)

@AnnounceMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取维护公告的图片：

    Example：-维护公告
    """
    if args.extract_plain_text() != "":
        return
    image_path = build_path(ASSETS, ["image", "jx3", "update.png"])
    if os.path.exists(image_path):
        img = Request(Path(image_path).as_uri()).local_content
        await AnnounceMatcher.finish(ms.image(img))
    else:
        img = await get_image()
        await AnnounceMatcher.finish(img)

BetaAnnounceMatcher = on_command("jx3_beta_announce", aliases={"体服公告", "体服更新"}, priority=5, force_whitespace=True)

@BetaAnnounceMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取体服维护公告。
    """
    if args.extract_plain_text() != "":
        return
    img = await get_image(ver="latest_exp")
    await BetaAnnounceMatcher.finish(img)