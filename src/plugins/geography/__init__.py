from .typhoon import *

tyList = on_command("typhoon_list", aliases={"台风列表"}, priority=5)


@tyList.handle()
async def _(event: GroupMessageEvent):
    data = await get_typhoon_list()
    if data:
        msg = "、".join(data)
        return await tyList.finish(f"当前西北太平洋有以下台风：\n{msg}")
    else:
        return await tyList.finish("当前西北太平洋洋面并无台风。")

tyPath = on_command("typhoon_path", aliases={"台风路径"}, priority=5)


@tyPath.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    tyName = args.extract_plain_text()
    data = await get_typhoon_path(tyName)
    if type(data) == type([]):
        return await tyPath.finish(data[0])
    else:
        return await tyPath.finish(ms.image(data))

tyNews = on_command("typhoon_news", aliases={"台风快讯"}, priority=5)


@tyNews.handle()
async def _(event: GroupMessageEvent):
    msg = await get_typhoon_news()
    return await tyNews.finish(msg)

fy4a = on_command("fy4a", aliases={"卫星云图"}, priority=5)
# 数据源：中央气象台 风云四号卫星 真彩图


@fy4a.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    img = await fy4a_true_color()
    return await fy4a.finish(ms.image(img))
