from .api import *

dh_ = on_command("jx3_dh", aliases={"蹲号"}, priority=5)


@dh_.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    """
    获取盆栽蹲号信息：

    Example：-蹲号 蝶金
    """
    details = args.extract_plain_text()
    if details == "":
        await dh_.finish("您没有输入条件哦，请检查后重试~\n条件以空格分割哦~")
    details = details.split(" ")
    if len(details) < 1:
        await dh_.finish("您没有输入条件哦，请检查后重试~\n条件以空格分割哦~")
    final_details = ",".join(details)
    data = await get_dh(final_details)
    if type(data) == type([]):
        image = data[0]
        links = data[1]
        state["links"] = links
        await dh_.send(ms.image(image))
        return
    else:
        await dh_.finish(data)

@dh_.got("num", prompt="回复标题前方的序号，音卡就可以给你链接啦！")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    num = num.extract_plain_text()
    if not checknumber(num):
        await dh_.finish(PROMPT_NumberInvalid)
    else:
        links = state["links"]
        await dh_.finish(links[int(num)-1])
    