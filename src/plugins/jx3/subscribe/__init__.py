from .api import *

jx3_cmd_subscribe = on_command("jx3_subscribe", aliases={"订阅"}, priority=5)

@jx3_cmd_subscribe.handle()
async def jx3_subscribe(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    订阅内容，可选择订阅的内容：

    目前支持：玄晶、新闻、开服、更新。

    Example：-订阅 玄晶

    Notice：一次只可订阅一个。
    '''
    now = load_or_write_subscribe(event.group_id)
    template = [Jx3Arg(Jx3ArgsType.default), Jx3Arg(Jx3ArgsType.default)]
    arg_sub, arg_info = get_args(args.extract_plain_text(), template)
    if arg_sub not in VALID_Subjects:
        return await jx3_cmd_subscribe.finish("请不要订阅一些很奇怪的东西，我可是无法理解的哦~")
    if arg_sub in now:
        return await jx3_cmd_subscribe.finish("已经订阅了哦，请不要重复订阅~")
    now[arg_sub] = {'arg': arg_info} if arg_info else {}
    load_or_write_subscribe(event.group_id, now)
    return await jx3_cmd_subscribe.finish(f"已开启本群的{arg_sub}订阅！当收到事件时会自动推送，如需取消推送，请发送：-退订 {arg_sub}")

jx3_cmd_unsubscribe = on_command("jx3_unsubscribe", aliases={"退订"}, priority=5)

@jx3_cmd_unsubscribe.handle()
async def jx3_unsubscribe(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    退订某内容，可选择：

    同上。

    Example：-退订 开服
    '''
    now = load_or_write_subscribe(event.group_id)
    template = [Jx3Arg(Jx3ArgsType.default), Jx3Arg(Jx3ArgsType.default)]
    arg_sub, arg_info = get_args(args.extract_plain_text(), template)
    if arg_sub not in VALID_Subjects:
        return await jx3_cmd_unsubscribe.finish("请不要取消订阅一些很奇怪的东西，我可是无法理解的哦~")
    if arg_sub not in now:
        return await jx3_cmd_unsubscribe.finish("尚未订阅，无法取消订阅哦~")
    del now[arg_sub]
    load_or_write_subscribe(event.group_id, now)
    return await jx3_cmd_unsubscribe.finish(f"已关闭本群的{arg_sub}订阅！如需再次开启，请发送：\n-订阅 {arg_sub}")
