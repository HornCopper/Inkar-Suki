from .api import *

dh_ = on_command("jx3_dh", aliases = {"蹲号"}, priority = 5)
@dh_.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取盆栽蹲号信息：

    Example：-蹲号 蝶金
    """
    details = args.extract_plain_text()
    if details == "":
        await dh_.finish("您没有输入条件哦，请检查后重试~\n条件以英文分号(;)分割哦~")
    details = details.split(";")
    if len(details) < 1:
        await dh_.finish("您没有输入条件哦，请检查后重试~\n条件以英文分号(;)分割哦~")
    final_details = ",".join(details)
    data = await get_dh(final_details)
    if type(data) != type([]):
        await dh_.finish(data)
    else:
        await bot.call_api("send_group_forward_msg", group_id = event.group_id, messages = data)