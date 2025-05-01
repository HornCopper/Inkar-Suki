from pathlib import Path

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment as ms

from src.const.prompts import PROMPT
from src.const.jx3.kungfu import Kungfu

from .macro import get_macro
from .martix import get_matrix
from .qixue import get_qixue
from .skill import get_skill

macro_matcher = on_command("jx3_macro_v2", aliases={"宏"}, force_whitespace=True, priority=5)

@macro_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    kungfu = Kungfu(args.extract_plain_text()).name
    if kungfu is None:
        await macro_matcher.finish("唔……心法输入有误，请检查后重试~")
    data = await get_macro(kungfu)
    await macro_matcher.finish(data)

matrix_matcher = on_command("jx3_matrix", aliases={"阵眼"}, force_whitespace=True, priority=5)

@matrix_matcher.handle()
async def _(args: Message = CommandArg()):
    """
    查询阵眼效果：

    Example：-阵眼 紫霞功
    """
    if args.extract_plain_text() == "":
        return
    if args.extract_plain_text():
        msg = await get_matrix(Kungfu(args.extract_plain_text()))
        await matrix_matcher.finish(msg)
    else:
        await matrix_matcher.finish("没有输入任何心法名称哦，没办法帮你找啦。")

talent_matcher = on_command("jx3_qixue", aliases={"奇穴"}, force_whitespace=True, priority=5)

@talent_matcher.handle()
async def _(argument: Message = CommandArg()):
    """
    查询奇穴。
    """
    args = argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2, 3]:
        await talent_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：奇穴 <心法> [关键词] [赛季]")
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
        await talent_matcher.finish(ms.image(msg.as_uri()))
    else:
        await talent_matcher.finish(msg)

skill_matcher = on_command("jx3_skill", aliases={"技能"}, force_whitespace=True, priority=5)

@skill_matcher.handle()
async def _(argument: Message = CommandArg()):
    """
    查询技能。
    """
    args = argument.extract_plain_text().split(" ")
    if len(args) != 2:
        await skill_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：技能 <心法> <关键词>")
    kungfu = args[0]
    skill = args[1]
    msg = await get_skill(kungfu, skill)
    await skill_matcher.finish(msg)