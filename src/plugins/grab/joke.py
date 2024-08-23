from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent

import httpx

api = "https://api.qicaiyun.top/joke/api.php"

async def get_joke() -> str:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(api)
        resp.encoding = "gbk"
        data = resp.text
        msg = data.split("、")[1:]
        return str(msg)

rdcoldjoke = on_command("冷笑话", priority=5, force_whitespace=True)

@rdcoldjoke.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    msg = await get_joke()
    await rdcoldjoke.finish(msg)