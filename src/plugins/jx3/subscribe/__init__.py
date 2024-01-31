from .renderer import *

jx3_cmd_subscribe = on_command(
    "jx3_subscribe",
    aliases={"订阅"},
    priority=5,
    catalog=permission.jx3.common.event.subscribe,
    description="订阅",
    example=[
        Jx3Arg(Jx3ArgsType.subscribe),
        Jx3Arg(Jx3ArgsType.string, alias="子分类", is_optional=True),
    ],
    document="""订阅内容，可选择订阅的内容：
    Example：订阅 玄晶 [级别]
    Notice：订阅多个时用[/]斜杠分开。""",
)


async def get_jx3_subscribe(event: GroupMessageEvent, args: list[Any]):
    arg_subs, arg_info = args
    subscribe_dict = GroupConfig(event.group_id).mgr_property("subscribe")
    if arg_subs is None:
        msg = f"没有[{str(event.message)}]这样的主题可以订阅，请检查一下哦。"
    else:
        for arg_sub in arg_subs:
            subscribe_dict[arg_sub] = {"arg": arg_info} if arg_info else {}
            GroupConfig(event.group_id).mgr_property("subscribe", subscribe_dict)  # 需要初始化
        subs = str.join("/", arg_subs)
        msg = f"已开启本群的[{subs}(级别{arg_info or 0})]订阅！\n当收到事件时会自动推送，如需取消推送，请发送：退订 {subs}"
    return subscribe_dict, arg_subs, msg


@jx3_cmd_subscribe.handle()
async def jx3_subscribe(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    subscribe_dict, subject_names, msg = await get_jx3_subscribe(event, args)
    subjects = [VALID_Subjects.get(subject_name) for subject_name in subject_names]
    result = await render_subscribe(VALID_Subjects, subscribe_dict, subjects, msg)
    return await jx3_cmd_subscribe.finish(ms.image(Path(result).as_uri()))


async def get_jx3_unsubscribe(event: GroupMessageEvent, arg_subs: list[str]):
    subscribe = GroupConfig(event.group_id).mgr_property("subscribe")
    for arg_sub in arg_subs:
        if arg_sub in subscribe:
            del subscribe[arg_sub]
    subs = str.join("/", arg_subs)
    msg = f"已关闭本群的[{subs}]订阅！\n如需再次开启，请发送：[订阅 {subs}]"
    return subscribe, arg_subs, msg


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
    Example：退订 开服
    """,
)


@jx3_cmd_unsubscribe.handle()
async def jx3_unsubscribe(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_subs,  = args
    if not arg_subs:
        return await jx3_cmd_unsubscribe.finish("未找到这样的主题，检查一下哦~")

    subscribe_dict, subject_names, msg = await get_jx3_unsubscribe(event, arg_subs)
    subject = [VALID_Subjects.get(subject_name) for subject_name in subject_names]
    result = await render_subscribe(VALID_Subjects, subscribe_dict, subject, msg)
    return await jx3_cmd_unsubscribe.finish(ms.image(Path(result).as_uri()))
