from .api import *

announce = on_command("jx3_announce", aliases={"维护公告", "更新公告", "公告", "更新"}, priority=5)


@announce.handle()
async def _(event: GroupMessageEvent):
    """
    获取维护公告的图片：

    Example：-维护公告
    """
    url = await announce_()
    await announce.finish(ms.image(url))
