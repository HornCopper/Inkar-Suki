from .api import *

jx3_cmd_saohua_random = on_command("jx3_random", aliases={"骚话", "烧话"}, priority=5)


@jx3_cmd_saohua_random.handle()
async def jx3_saohua_random():
    """
    召唤一条骚话：

    Example：-骚话
    """
    full_link = f"https://www.jx3api.com/data/saohua/random?token={token}"
    info = await get_api(full_link)
    msg = info["data"]["text"]
    await jx3_cmd_saohua_random.finish(msg)

jx3_cmd_saohua_tiangou = on_command("jx3_tiangou", aliases={"舔狗"}, priority=5)


@jx3_cmd_saohua_tiangou.handle()
async def jx3_saohua_tiangou():
    """
    获取一条舔狗日志：

    Example：-舔狗
    """
    full_link = f"https://www.jx3api.com/data/saohua/content?token={token}"
    info = await get_api(full_link)
    msg = info["data"]["text"]
    await jx3_cmd_saohua_tiangou.finish(msg)