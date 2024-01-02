from .api import *

jx3_cmd_arena_records = on_command("jx3_arena_records", aliases={"战绩", "名剑战绩"}, priority=5)


@jx3_cmd_arena_records.handle()
async def jx3_carena_records(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    template = [
        Jx3Arg(Jx3ArgsType.server),
        Jx3Arg(Jx3ArgsType.user),
        Jx3Arg(Jx3ArgsType.default, default='22')
    ]
    server, user, pvp_mode = get_args(args, template, event)
    if server is None:
        return await jx3_cmd_arena_records.finish(PROMPT_ServerNotExist)
    if user is None:
        return await jx3_cmd_arena_records.finish(PROMPT_UserNotExist)

    data = await arena_records(object="战绩", server=server, name=user, mode=pvp_mode)
    if type(data) == type([]):
        return await jx3_cmd_arena_records.finish(data[0])
    return await jx3_cmd_arena_records.finish(ms.image(data))


jx3_cmd_arena_rank = on_command("jx3_arena_rank", aliases={"排行", "名剑排行"}, priority=5)


@jx3_cmd_arena_records.handle()
async def jx3_arena_records(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    template = [Jx3Arg(Jx3ArgsType.default, default='22')]
    pvp_mode, = get_args(args, template, event)
    data = await arena_rank(mode=pvp_mode)
    if type(data) == type([]):
        return await jx3_cmd_arena_records.finish(data[0])
    return await jx3_cmd_arena_records.finish(ms.image(data))

jx3_cmd_arena_statistics = on_command("jx3_arena_statistics", aliases={"统计", "名剑统计"}, priority=5)


@jx3_cmd_arena_records.handle()
async def jx3_arena_records(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    template = [Jx3Arg(Jx3ArgsType.default, default='22')]
    pvp_mode, = get_args(args, template, event)
    data = await arena_statistics(mode=pvp_mode)
    if type(data) == type([]):
        return await jx3_cmd_arena_records.finish(data[0])
    else:
        return await jx3_cmd_arena_records.finish(ms.image(data))
