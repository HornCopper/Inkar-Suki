from .chutian import *
from .yuncong import *

cts = on_command("jx3_chutian", aliases={"楚天社"}, priority=5)

@cts.handle()
async def _(event: GroupMessageEvent):
    image = await getChutianImg()
    await cts.finish(ms.image(image))

ycs = on_command("jx3_yuncong", priority=5, aliases={"云从社"})

@ycs.handle()
async def _(event: GroupMessageEvent):
    return # 正在施工