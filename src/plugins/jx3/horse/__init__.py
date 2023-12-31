from .api import *

ct = on_command(
    "jx3_ct",
    aliases={"赤兔"},
    priority=5,
    description='获取赤兔刷新信息',
    catalog='jx3.pvx.property.horse.chitu',
    example=[Jx3ArgsType.server],
    document='''数据来源于剑三盒子
    获取当前各个地图马场的数据并整合
    得到马儿所在的地图'''
)


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
