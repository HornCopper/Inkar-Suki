from pathlib import Path

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from src.const.jx3.kungfu import Kungfu

from .macro import get_macro
from .martix import get_matrix
from .qixue import get_qixue

MacroMatcher = on_command("jx3_macro_v2", aliases={"宏"}, force_whitespace=True, priority=5)

@MacroMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    kungfu = Kungfu(args.extract_plain_text()).name
    if kungfu is None:
        await MacroMatcher.finish("唔……心法输入有误，请检查后重试~")
    data = await get_macro(kungfu)
    await MacroMatcher.finish(data)

MatrixMatcher = on_command("jx3_matrix", aliases={"阵眼"}, force_whitespace=True, priority=5)

@MatrixMatcher.handle()
async def _(args: Message = CommandArg()):
    """
    查询阵眼效果：

    Example：-阵眼 紫霞功
    """
    if args.extract_plain_text() == "":
        return
    if args.extract_plain_text():
        msg = await get_matrix(Kungfu(args.extract_plain_text()))
        await MatrixMatcher.finish(msg)
    else:
        await MatrixMatcher.finish("没有输入任何心法名称哦，没办法帮你找啦。")

QixueMatcher = on_command("jx3_qixue", aliases={"奇穴"}, force_whitespace=True, priority=5)

@QixueMatcher.handle()
async def _(argument: Message = CommandArg()):
    """
    查询奇穴。
    """
    args = argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2, 3]:
        await QixueMatcher.finish("唔……格式错误，请参考下面的格式：\n奇穴 心法 奇穴 赛季\n赛季非必须，可以省略。")
    if len(args) == 3:
        kungfu = args[0]
        qixue = args[1]
        season = args[2]
    elif len(args) == 2:
        kungfu = args[0]
        qixue = args[1]
        season = ""
    elif len(args) == 1:
        kungfu = args[0]
        qixue = ""
        season = ""
    msg = await get_qixue(qixue, kungfu, season)
    if isinstance(msg, Path):
        await QixueMatcher.finish(ms.image(msg.as_uri()))
    else:
        await QixueMatcher.finish(msg)