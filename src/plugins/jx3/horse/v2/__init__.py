from ..api import *
from .renderer import *
from .api import *

jx3_cmd_horseinfo_map = on_command(
    "抓马",
    aliases={"马场"},
    priority=5,
    description='获取各个马场刷新信息',
    catalog=permission.jx3.pvx.property.horse.info,
    example=[
        Jx3Arg(Jx3ArgsType.server, is_optional=True),
        Jx3Arg(Jx3ArgsType.string, default=None, alias='马名')
    ],
    document='''数据来源于剑三盒子
    获取当前各个地图马场的数据并整合
    得到马儿所在的地图'''
)


@jx3_cmd_horseinfo_map.handle()
async def jx3_horseinfo(template: list[Any] = Depends(Jx3Arg.arg_factory)):
    return await get_jx3_horse_info_view(jx3_cmd_horseinfo_map, template)


async def get_jx3_horse_info_view(matcher: Matcher, template: list[Any]):
    view_models = await get_jx3_horse_info(template)
    if isinstance(view_models, list):
        return await matcher.finish(view_models[0])

    result = await render_items(*view_models)
    img = ms.image(Path(result).as_uri())
    return await matcher.send(img)


async def get_jx3_horse_info(template: list[Any]):
    arg_server, arg_horse = template
    if not arg_server:
        return [PROMPT_ServerNotExist]
    reporter = await get_horse_reporter(arg_server)
    if isinstance(reporter, str):
        return [reporter]

    horse_record, map_data, horse_data = reporter

    if arg_horse:
        # TODO use 责任链
        horse_record = [x for x in horse_record if arg_horse in x.horses_id]
        horse_data = [x for x in horse_data if arg_horse == x.key]
        map_data = [x.map_data for x in horse_record]
        map_data = extensions.distinct(map_data, lambda x: x.map_id)

    return (
        arg_server,
        [x.to_dict() for x in horse_record],
        [x.to_dict() for x in map_data],
        [x.to_dict() for x in horse_data],
    )


@scheduler.scheduled_job("interval", id='jx3_update_horseinfo', seconds=3600*(1-0.05*random.random()))
async def jx3_update_horseinfo():
    servers = list(server_map)
    server = random.choice(servers)
    await get_horse_reporter(server)
