from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg

from .api import get_exam_answer

exam_matcher = on_command("jx3_exam", aliases={"科举"}, force_whitespace=True, priority=5)

@exam_matcher.handle()
async def _(args: Message = CommandArg()):
    """
    查询科举答案：

    Example：-科举 古琴有几根弦
    """
    if args.extract_plain_text() == "":
        return
    if args.extract_plain_text():
        await exam_matcher.finish(await get_exam_answer(args.extract_plain_text()))
    else:
        await exam_matcher.finish("没有提供科举的问题，没办法解答啦。")
