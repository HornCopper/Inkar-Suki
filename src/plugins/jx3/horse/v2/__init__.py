from ..api import *
from .renderer import *
from .api import *
jx3_cmd_horseinfo_chitu = on_command(
    "赤兔",
    aliases={},
    priority=5,
    description='[暂未开放]获取赤兔刷新信息',
    catalog='jx3.pvx.property.horse.chitu',
    example=[
        Jx3Arg(Jx3ArgsType.server)
    ],
    document='''数据来源于剑三盒子
    获取当前各个地图马场的数据并整合
    得到马儿所在的地图'''
)


@jx3_cmd_horseinfo_chitu.handle()
async def jx3_horseinfo_chitu(event: GroupMessageEvent, template: list[Jx3Arg] = Depends(Jx3Arg.arg_factory)):
    """
    获取赤兔刷新信息：

    Example：-赤兔 幽月轮
    """
    pass

jx3_cmd_horseinfo_map = on_command(
    "抓马",
    aliases={"马场"},
    priority=5,
    description='获取各个马场刷新信息',
    catalog='jx3.pvx.property.horse.common',
    example=[
        Jx3Arg(Jx3ArgsType.server)
    ],
    document='''数据来源于剑三盒子
    获取当前各个地图马场的数据并整合
    得到马儿所在的地图'''
)


@jx3_cmd_horseinfo_map.handle()
async def jx3_horseinfo(event: GroupMessageEvent, template: list[Jx3Arg] = Depends(Jx3Arg.arg_factory)):
    server, = template
    reporter = await get_horse_reporter(server)
    if isinstance(reporter, str):
        return await jx3_cmd_horseinfo_map.finish(reporter)

    horse_record, map_data, horse_data = reporter
    result = await render_items(
        server,
        [x.to_dict() for x in horse_record],
        [x.to_dict() for x in map_data],
        [x.to_dict() for x in horse_data],
    )
    img = ms.image(Path(result).as_uri())
    return await jx3_cmd_horseinfo_map.send(img)
