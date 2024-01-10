from .api import *

jx3_cmd_daily_img = on_command(
    "jx3_daily_img",
    aliases={"日常图", "周常图"},
    priority=5,
    document="""
    查询日常。

    Notice：每个服务器的日常相同，仅美人图有可能存在不同。

    Example：-日常
    Example：-周常
    Example：-日常 幽月轮
    """
)


@jx3_cmd_daily_img.handle()
async def jx3_daily_img(event: GroupMessageEvent, args: Message = CommandArg()):
    img = await daily_(args.extract_plain_text(), group_id=event.group_id)
    if isinstance(img, list):
        return await jx3_cmd_daily_img.finish(img[0])
    return await jx3_cmd_daily_img.finish(ms.image(img))


jx3_cmd_daily_txt = on_command(
    "jx3_daily_txt",
    aliases={"日常", "周常"},
    priority=5,
    example=[
        Jx3Arg(Jx3ArgsType.server, is_optional=True),
        Jx3Arg(Jx3ArgsType.bool, is_optional=True, alias='要不要骚话'),
    ],
    document="""
    查询日常。

    Notice：每个服务器的日常相同，仅美人图有可能存在不同。

    Example：-日常
    Example：-周常
    Example：-日常 幽月轮
    """
)


@jx3_cmd_daily_txt.handle()
async def jx3_daily_txt(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_server, arg_need_saohua = args
    content = await daily_txt(arg_server, group_id=event.group_id)
    suffix = (await saohua()) if arg_need_saohua else ''
    return await jx3_cmd_daily_txt.finish(f'{content.text}{suffix}')
