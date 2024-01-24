from .api import *

announce = on_command("jx3_announce", aliases={"维护公告v1", "更新公告v1", "公告v1", "更新v1"}, priority=5)

@announce.handle()
async def _(event: GroupMessageEvent):
    """
    获取维护公告的图片：

    Example：-维护公告
    """
    url = await announce_by_jx3api()
    return await announce.finish(ms.image(url))
