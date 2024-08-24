from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from src.tools.utils.num import check_number
from src.tools.basic.prompts import PROMPT

from .api import *

task_ = on_command("jx3_task", aliases={"任务"}, force_whitespace=True, priority=5)


@task_.handle()
async def _(state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    """
    查询任务及任务链：

    Example：-任务 十万火急
    """
    task__ = args.extract_plain_text()
    data = await getTask(task__)
    if data["status"] == 404:
        await task_.finish("未找到该任务，请检查后重试~")
    map = data["map"]
    id = data["id"]
    task___ = data["task"]
    target = data["target"]
    level = data["level"]
    state["map"] = map
    state["id"] = id
    state["task"] = task___
    state["target"] = target
    state["level"] = level
    msg = ""
    if not isinstance(map, list) or not isinstance(task___, dict):
        return
    for i in range(len(map)):
        msg = msg + f"{i}.{map[i]}：{task___[i]}\n"
    msg = msg[:-1]
    await task_.send(msg)


@task_.got("num", prompt="发送序号以搜索，发送其他内容则取消搜索。")
async def _(state: T_State, num: Message = Arg()):
    num_ = num.extract_plain_text()
    if check_number(num_):
        num_ = int(num_)
        map = state["map"][num_]
        id = state["id"][num_]
        task__ = state["task"][num_]
        target = state["target"][num_]
        level = state["level"][num_]
        msg = f"查询到「{task__}」：\nhttps://www.jx3box.com/quest/view/{id}\n开始等级：{level}\n地图：{map}\n任务目标：{target}"
        chain = await getTaskChain(id)
        msg = msg + f"\n任务链：{chain}"
        await task_.finish(msg)
    else:
        await task_.finish(PROMPT.NumberInvalid)
