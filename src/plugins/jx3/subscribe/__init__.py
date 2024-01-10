from .renderer import *

jx3_cmd_subscribe = on_command(
    "jx3_subscribe",
    aliases={"订阅"},
    priority=5,
    catalog=permission.jx3.common.event.subscribe,
    description="订阅",
    example=[
        Jx3Arg(Jx3ArgsType.subscribe),
        Jx3Arg(Jx3ArgsType.string, alias='子分类', is_optional=True),
    ],
    document='''订阅内容，可选择订阅的内容：
    Example：订阅 玄晶 [级别]
    Notice：一次只可订阅一个。''',
)


async def get_jx3_subscribe(event: GroupMessageEvent, args: list[Any]):
    arg_sub, arg_info = args
    subscribe_dict = GroupConfig(event.group_id).mgr_property('subscribe')
    if arg_sub is None:
        msg = f"没有[{arg_sub}]这样的主题可以订阅，请检查一下哦。"
    else:
        subscribe_dict[arg_sub] = {"arg": arg_info} if arg_info else {}
        msg = f"已开启本群的[{arg_sub}(级别{arg_info or 0})]订阅！\n当收到事件时会自动推送，如需取消推送，请发送：退订 {arg_sub}"
    return subscribe_dict, arg_sub, msg


@jx3_cmd_subscribe.handle()
async def jx3_subscribe(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    subscribe_dict, subject_name, msg = await get_jx3_subscribe(event, args)
    subject = VALID_Subjects.get(subject_name)
    result = await render_subscribe(VALID_Subjects, subscribe_dict, subject, msg)
    return await jx3_cmd_subscribe.finish(ms.image(Path(result).as_uri()))


async def get_jx3_unsubscribe(event: GroupMessageEvent, arg_sub: str):
    subscribe = GroupConfig(event.group_id).mgr_property('subscribe')
    if arg_sub is None:
        msg = f"没有这样的主题可以退订，请检查一下哦。"
    elif arg_sub not in subscribe:
        msg = f"尚未订阅[{arg_sub}]，取消不了。"
    else:
        del subscribe[arg_sub]
        msg = f"已关闭本群的{arg_sub}订阅！\n如需再次开启，请发送：订阅 {arg_sub}"
    return subscribe, arg_sub, msg


jx3_cmd_unsubscribe = on_command(
    "jx3_unsubscribe",
    aliases={"退订"},
    priority=5,
    catalog=permission.jx3.common.event.subscribe,
    description="退订",
    example=[
        Jx3Arg(Jx3ArgsType.subscribe),
    ],
    document="""
    退订某内容，可选择：

    同上。

    Example：退订 开服
    """,
)


@jx3_cmd_unsubscribe.handle()
async def jx3_unsubscribe(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_sub,  = args
    now, subject, msg = await get_jx3_unsubscribe(event, arg_sub)
    result = await render_subscribe(VALID_Subjects, now, subject, msg)
    return await jx3_cmd_unsubscribe.finish(ms.image(Path(result).as_uri()))
