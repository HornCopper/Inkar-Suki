from .api import *

buff_ = on_command("jx3_buff", aliases = {"debuff","buff"}, priority = 5)
@buff_.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    """
    获取Buff信息：

    Example：-buff 躺在冰冷的地上
    Example：-debuff 耐力受损
    """
    buff = args.extract_plain_text()
    data = await get_buff(buff)
    if type(data) != type("sb"):
        state["icon"] = data["icon"]
        state["remark"] = data["remark"]
        state["desc"] = data["desc"]
        state["name"] = data["name"]
        state["id"] = data["id"]
        msg = ""
        for i in range(len(data["icon"])):
            msg = msg + "\n" + str(i) + "." + data["name"][i] + "（技能ID：" + data["id"][i] + "）"
        await buff_.send(msg[1:])
        return
    else:
        await buff_.finish(data)

@buff_.got("num", prompt = "输入数字搜索状态效果，输入其他内容则无视。")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    num = num.extract_plain_text()
    if checknumber(num):
        icon = state["icon"]
        remark = state["remark"]
        desc = state["desc"]
        name = state["name"]
        id = state["id"]
        if int(num) not in list(range(len(icon))):
            await buff_.finish("唔，输入的数字不对哦，取消搜索~")
        else:
            num = int(num)
            msg = ms.image(icon[num]) + f"\nBUFF名称：{name[num]}\n{desc[num]}\n特殊描述：{remark[num]}"
            await buff_.finish(msg)
    else:
        return
