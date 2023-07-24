from .api import *

exam = on_command("jx3_exam", aliases={"科举"}, priority=5)


@exam.handle()
async def _(args: Message = CommandArg()):
    """
    查询科举答案：

    Example：-科举 古琴有几根弦
    """
    if args.extract_plain_text():
        await exam.finish(await exam_(args.extract_plain_text()))
    else:
        await exam.finish("没有提供科举的问题，没办法解答啦。")
