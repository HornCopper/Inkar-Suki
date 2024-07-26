from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg

from .api import *

matrix = on_command("jx3_matrix", aliases={"阵眼"}, force_whitespace=True, priority=5)


@matrix.handle()
async def _(args: Message = CommandArg()):
    """
    查询阵眼效果：

    Example：-阵眼 紫霞功
    """
    if args.extract_plain_text() == "":
        return
    if args.extract_plain_text():
        await matrix.finish(await matrix_(args.extract_plain_text()))
    else:
        await matrix.finish("没有输入任何心法名称哦，没办法帮你找啦。")
