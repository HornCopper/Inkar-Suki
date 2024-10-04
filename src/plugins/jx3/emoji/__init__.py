from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.utils.network import Request

import random

EmojiMatcher = on_command("jx3_emoji", aliases={"随机表情"}, force_whitespace=True, priority=5)


@EmojiMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    api = "https://cms.jx3box.com/api/cms/post/emotions?type=&search=&star=&original=&page=1&per=50"
    data = (await Request(api).get()).json()
    data = data["data"]["list"]
    failed_time = 0
    while True:
        rdnum = random.randint(0, len(data) - 1)
        response = (await Request(data[rdnum]["url"]).get())
        if response.status_code == 200:
            await EmojiMatcher.finish(ms.image(data[rdnum]["url"]))
        else:
            failed_time = failed_time + 1
            if failed_time == 5:
                await EmojiMatcher.finish("唔……已经失败超过5次，查找失败！")
            continue
