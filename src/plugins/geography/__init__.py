from .typhoon import *

tyList = on_command("typhoon_list", aliases={"台风列表"}, priority=5)

@tyList.handle()
async def _(event: GroupMessageEvent):
    data = await get_typhoon_list()
    if not data:
        msg = "、".join(data)
        await tyList.finish(f"当前西北太平洋有以下台风：\n{msg}")
    else:
        await tyList.finish("当前西北太平洋洋面并无台风。")

tyPath = on_command("typhoon_path", aliases={"台风路径"}, priority=5)

@tyPath.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    tyName = args.extract_plain_text()
    data = await get_typhoon_path(tyName)
    if type(data) == type([]):
        await tyPath.finish(data[0])
    else:
        await tyPath.finish(ms.image(data))

tyNews = on_command("typhoon_news", aliases={"台风快讯"}, priority=5)

@tyNews.handle()
async def _(event: GroupMessageEvent):
    msg = await get_typhoon_news()
    await tyNews.finish(msg)