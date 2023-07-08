from .api import *
from .renderer import *
jx3_cmd_subscribe = on_command("jx3_subscribe", aliases={"订阅"}, priority=5)


async def get_jx3_subscribe(event: GroupMessageEvent, args: Message = CommandArg()):
    now = load_or_write_subscribe(event.group_id)
    template = [Jx3Arg(Jx3ArgsType.default), Jx3Arg(Jx3ArgsType.default)]
    arg_sub, arg_info = get_args(args.extract_plain_text(), template)
    arg_sub = arg_sub.lower() if arg_sub else None
    subject = VALID_Subjects.get(arg_sub)
    if subject is None:
        msg = f'没有[{arg_sub}]这样的主题可以订阅，请检查一下哦。'
    else:
        now[arg_sub] = {'arg': arg_info} if arg_info else {}
        load_or_write_subscribe(event.group_id, now)
        msg = f'已开启本群的[{arg_sub}(级别{arg_info or 0})]订阅！\n当收到事件时会自动推送，如需取消推送，请发送：退订 {arg_sub}'
    return now, subject, msg


@jx3_cmd_subscribe.handle()
async def jx3_subscribe(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    订阅内容，可选择订阅的内容：
    Example：订阅 玄晶 [级别]

    Notice：一次只可订阅一个。
    '''
    now, subject, msg = await get_jx3_subscribe(event, args)

    result = await render_subscribe(VALID_Subjects, now, subject, msg)
    return await jx3_cmd_subscribe.finish(ms.image(Path(result).as_uri()))

jx3_cmd_unsubscribe = on_command("jx3_unsubscribe", aliases={"退订"}, priority=5)


async def get_jx3_unsubscribe(event: GroupMessageEvent, args: Message = CommandArg()):
    now = load_or_write_subscribe(event.group_id)
    template = [Jx3Arg(Jx3ArgsType.default), Jx3Arg(Jx3ArgsType.default)]
    arg_sub, arg_info = get_args(args.extract_plain_text(), template)
    arg_sub = arg_sub.lower() if arg_sub else None
    subject = VALID_Subjects.get(arg_sub)
    if subject is None:
        msg = f'没有[{arg_sub}]这样的主题可以退订，请检查一下哦。'
    elif arg_sub not in now:
        msg = f'尚未订阅[{arg_sub}]，取消不了。'
    else:
        del now[arg_sub]
        load_or_write_subscribe(event.group_id, now)
        msg = f'已关闭本群的{arg_sub}订阅！\n如需再次开启，请发送：订阅 {arg_sub}'
    return now, subject, msg


@jx3_cmd_unsubscribe.handle()
async def jx3_unsubscribe(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    退订某内容，可选择：

    同上。

    Example：退订 开服
    '''
    now, subject, msg = await get_jx3_unsubscribe(event, args)
    result = await render_subscribe(VALID_Subjects, now, subject, msg)
    return await jx3_cmd_unsubscribe.finish(ms.image(Path(result).as_uri()))
