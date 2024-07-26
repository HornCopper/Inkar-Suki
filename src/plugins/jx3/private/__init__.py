from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from src.tools.utils.request import get_content

from .api import *

import os

dilu = on_command("jx3_dilu", aliases={"的卢统计"}, force_whitespace=True, priority=5)


@dilu.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    img = await get_dilu_data()
    await dilu.finish(ms.image(img))


monsters_v1 = on_command("jx3_monsters_v1", aliases={"百战"}, force_whitespace=True, priority=5)

@monsters_v1.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    correct_path = ASSETS + "/jx3/monsters.jpg"
    if os.path.exists(correct_path):
        await monsters_v1.finish(ms.image(Path(correct_path).as_uri()))
    else:
        url = await get_baizhan_img()
        data = await get_content(url)
        with open(correct_path, mode="wb") as bz:
            bz.write(data)
        await monsters_v1.finish(ms.image(Path(correct_path).as_uri()))