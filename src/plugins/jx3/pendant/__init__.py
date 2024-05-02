from .api import *

pendents = on_command("jx3_pendents", aliases={"挂件"}, force_whitespace=True, priority=5)


@pendents.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    await pendents.finish(await pendant(name=args.extract_plain_text()))
