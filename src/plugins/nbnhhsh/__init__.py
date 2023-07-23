import httpx

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import CommandArg

nbnhhsh = on_command("nbnhhsh", aliases={"能不能好好说话"}, priority=5)

@nbnhhsh.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    content = args.extract_plain_text()
    from nonebot.log import logger
    url = "https://lab.magiconch.com/api/nbnhhsh/guess"
    data = {
        "text": content
    }
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.post(url, data=data)
        result = resp.json()[0]
        resp = result
        if "trans" not in list(resp):
            await nbnhhsh.finish("没有任何可能的结果哦~")
        else:
            results = resp["trans"]
            ans = "可能的结果有：\n" + "、".join(results)
            await nbnhhsh.finish(ans)
