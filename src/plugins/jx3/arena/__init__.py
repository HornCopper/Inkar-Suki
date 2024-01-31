from .api import *

jx3_cmd_arena_records = on_regex(
    r"^(/)?(名剑|jjc|竞技场)?(战绩|记录)",
    name="名剑战绩",
    priority=5,
    description="获取玩家竞技场的战绩记录",
    catalog=permission.jx3.pvp.jjc.records,
    example=[
        Jx3Arg(Jx3ArgsType.server, is_optional=True),
        Jx3Arg(Jx3ArgsType.user),
        Jx3Arg(Jx3ArgsType.pvp_mode, default="33")
    ],
    document="""战绩 玩家id 模式
    模式可以写22 33 55"""
)


@jx3_cmd_arena_records.handle()
async def jx3_arena_records(event: GroupMessageEvent, template: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_server, arg_user, arg_pvp_mode = template
    if arg_server is None:
        return await jx3_cmd_arena_records.finish(PROMPT_ServerNotExist)
    if arg_user is None:
        return await jx3_cmd_arena_records.finish(PROMPT_UserNotExist)

    data = await arena_records(server=arg_server, name=arg_user, mode=arg_pvp_mode)
    print(data)
    if isinstance(data, list):
        return await jx3_cmd_arena_records.finish(data[0])
    return await jx3_cmd_arena_records.send(ms.image(data))


jx3_cmd_arena_rank = on_regex(
    r"^(/)?(名剑|jjc|竞技场)?(排行|榜单|榜)",
    name="名剑排行",
    priority=5,
    description="获取竞技场的各Top50",
    catalog=permission.jx3.pvp.jjc.rank,
    example=[
        Jx3Arg(Jx3ArgsType.pvp_mode, is_optional=True),
    ],
    document="""排行 模式
    模式可以写22 33 55"""
)


@jx3_cmd_arena_rank.handle()
async def jx3_arena_rank(bot: Bot, event: GroupMessageEvent, template: list[Any] = Depends(Jx3Arg.arg_factory)):
    pvp_mode, = template
    data = await arena_rank(mode=pvp_mode)
    if isinstance(data, list):
        return await jx3_cmd_arena_rank.finish(data[0])
    return await jx3_cmd_arena_rank.send(ms.image(data))

jx3_cmd_arena_statistics = on_regex(
    r"^(/)?(名剑|jjc|竞技场)?(统计|日志)",
    name="名剑统计",
    priority=5,
    description="获取竞技场的各门派统计",
    catalog=permission.jx3.pvp.jjc.statistics,
    example=[
        Jx3Arg(Jx3ArgsType.pvp_mode, is_optional=True),
    ],
    document="""统计 模式
    模式可以写22 33 55"""
)


@jx3_cmd_arena_statistics.handle()
async def jx3_arena_statistics(bot: Bot, event: GroupMessageEvent, template: list[Any] = Depends(Jx3Arg.arg_factory)):
    pvp_mode, = template
    data = await arena_statistics(mode=pvp_mode)
    if isinstance(data, list):
        return await jx3_cmd_arena_statistics.finish(data[0])
    return await jx3_cmd_arena_statistics.send(ms.image(data))
