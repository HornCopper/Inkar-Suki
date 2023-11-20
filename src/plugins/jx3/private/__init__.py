from .api import *

dilu = on_command("jx3_dilu", aliases={"的卢统计"}, priority=5)


@dilu.handle()
async def _(event: GroupMessageEvent):
    img = await get_dilu_data()
    await dilu.finish(ms.image(img))
