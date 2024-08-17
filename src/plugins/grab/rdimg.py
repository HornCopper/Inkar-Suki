from pathlib import Path

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Event, MessageSegment as ms

from src.tools.utils.request import get_content, get_api
from src.tools.file import get_content_local
from src.tools.utils.path import PLUGINS

import random
import httpx

rdci = on_command("随机猫图", priority=5)

rddi = on_command("随机狗图", aliases={"随机lwx"}, priority=5)

@rdci.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    data = await get_api("https://api.thecatapi.com/v1/images/search?size=full")
    image = await get_content(data[0]["url"])
    await rdci.finish(ms.image(image))

@rddi.handle()
async def _(event: Event, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    rdint = random.randint(1, 100)
    if event.user_id in [1649157526, 1925648680]:
        if rdint >= 31:
            img = get_content_local(Path(PLUGINS + "/grab/lwx" + str(random.randint(1,4)) + ".jpg").as_uri())
            await rddi.finish(ms.image(img))
    if rdint <= 10:
        img = get_content_local(Path(PLUGINS + "/grab/lwx" + str(random.randint(1,4)) + ".jpg").as_uri())
        await rddi.finish(ms.image(img))
    data = await get_api("https://api.thedogapi.com/v1/images/search?size=full")
    image = await get_content(data[0]["url"])
    await rddi.finish(ms.image(image))

rdli = on_command("随机龙图", priority=5)

@rdli.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    async with httpx.AsyncClient(follow_redirects=True) as client:
        batch_choice = random.choice(["batch1/", "batch2/", "batch3/"])
        base_url = "https://git.acwing.com/Est/dragon/-/raw/main/"
        rdnum = random.randint(
            (
                int(batch_choice[-2])
                -1
            )*500+1,
            (
                int(batch_choice[-2])
                *500
            )
                )
        for ext in [".jpg", ".png", ".gif"]:
            image_url = f"{base_url}{batch_choice}dragon_{rdnum}_{ext}"
            resp = await client.get(image_url)
            if resp.status_code == 200:
                image = resp.content
                await rdli.finish(ms.image(image))