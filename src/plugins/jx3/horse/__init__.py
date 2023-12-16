from .api import *

ct = on_command("jx3_ct", aliases={"赤兔"}, priority=5)


@ct.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取赤兔刷新信息：

    Example：-赤兔 幽月轮
    """
    server = args.extract_plain_text()
    msg = await get_chitu(server, group_id=event.group_id)
    return await ct.finish(msg)

horse = on_command("jx3_horse", aliases={"抓马", "马场"}, priority=5)


@horse.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    server = args.extract_plain_text()
    msg = await get_horse_reporter(server, group_id=event.group_id)
    return await horse.finish(msg)
