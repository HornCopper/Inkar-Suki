from .api import *

jx3_cmd_saohua_random = on_command("jx3_random", aliases={"骚话", "烧话"}, priority=5)

@jx3_cmd_saohua_random.handle()
async def jx3_saohua_random():
    """
    召唤一条骚话：

    Example：-骚话
    """
    r_text, r_id = await saohua_random()
    await jx3_cmd_saohua_random.finish(f"推栏之{r_id}：{r_text}")

jx3_cmd_saohua_tiangou = on_command("jx3_tiangou", aliases={"舔狗"}, priority=5)

@jx3_cmd_saohua_tiangou.handle()
async def jx3_saohua_tiangou():
    """
    获取一条舔狗日志：

    Example：-舔狗
    """
    r_text, r_id = await saohua_tiangou()
    await jx3_cmd_saohua_tiangou.finish(f"舔狗日志之{r_id}：\n{r_text}")
