from ..api import *
from .chitu import *
jx3_cmd_ct = on_command(
    "jx3_ct",
    aliases={"赤兔v1"},
    priority=5,
    description='获取赤兔刷新信息',
    catalog='jx3.pvx.property.horse.chitu',
    example=[Jx3ArgsType.server],
    document='''数据来源于剑三盒子
    获取当前各个地图马场的数据并整合
    得到马儿所在的地图'''
)


@jx3_cmd_ct.handle()
async def jx3_ct(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取赤兔刷新信息：

    Example：-赤兔 幽月轮
    """
    server = args.extract_plain_text()
    msg = await get_chitu(server, group_id=event.group_id)
    return await jx3_cmd_ct.finish(msg)

jx3_cmd_horse = on_command("jx3_horse", aliases={"抓马v1", "马场v1"}, priority=5)


@jx3_cmd_horse.handle()
async def jx3_horse(event: GroupMessageEvent, args: Message = CommandArg()):
    server = args.extract_plain_text()
    msg = await get_horse_reporter(server, group_id=event.group_id)
    return await jx3_cmd_horse.finish(msg)
