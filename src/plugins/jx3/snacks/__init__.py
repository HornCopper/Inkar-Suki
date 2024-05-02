from .api import *

snack = on_command("jx3_snack", aliases={"小药"}, force_whitespace=True, priority=5)

@snack.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    name = args.extract_plain_text()
    data = await getSnack(name)
    await snack.finish(data)