from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from src.tools.utils.time import checknumber

from .api import *

buff_ = on_command("jx3_buff", aliases={"debuff", "buff"}, force_whitespace=True, priority=5)


@buff_.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    """
    获取Buff信息：

    Example：-buff 躺在冰冷的地上
    Example：-debuff 耐力受损
    """
    if args.extract_plain_text() == "":
        return
    buff = args.extract_plain_text()
    data = await get_buff(buff)
    if not isinstance(data, str):
        state["icon"] = data["icon"]
        state["remark"] = data["remark"]
        state["desc"] = data["desc"]
        state["name"] = data["name"]
        state["id"] = data["id"]
        msg = ""
        for i in range(len(data["icon"])):
            msg = msg + "\n" + str(i) + "." + data["name"][i] + "（技能ID：" + data["id"][i] + "）"
        await buff_.send(msg[1:])
    else:
        await buff_.finish(data)


@buff_.got("num", prompt="输入数字搜索状态效果，输入其他内容则无视。")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    num_ = num.extract_plain_text()
    if checknumber(num_):
        icon = state["icon"]
        remark = state["remark"]
        desc = state["desc"]
        name = state["name"]
        state["id"]
        if int(num_) not in list(range(len(icon))):
            await buff_.finish("唔，输入的数字不对哦，取消搜索~")
        else:
            num_ = int(num_)
            msg = ms.image(icon[num_]) + f"\nBUFF名称：{name[num_]}\n{desc[num_]}\n特殊描述：{remark[num_]}"
            await buff_.finish(msg)
    else:
        return
