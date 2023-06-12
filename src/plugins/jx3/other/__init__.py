from src.tools.dep.bot import *
from .api import *

pendents = on_command("jx3_pendents", aliases={"挂件"}, priority=5)
@pendents.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    await pendents.finish(await pendant(name = args.extract_plain_text()))