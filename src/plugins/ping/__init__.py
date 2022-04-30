import sys
import time
from typing import List

import nonebot
import psutil
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Event
import nonebot

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
from permission import checker, block

ping = on_command("ping", aliases={"测试"}, priority=5)


@ping.handle()
async def _(event: Event):
    if block(str(event.user_id)):
        return
    if checker(str(event.user_id), 1) == False:
        times = str("现在是" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n当前版本v0.7.3(Nonebot 2.0.0b1)")
        await ping.finish(times)

    def per_cpu_status() -> List[float]:
        return psutil.cpu_percent(interval=1, percpu=True)

    def memory_status() -> float:
        return psutil.virtual_memory().percent

    times = str("现在是" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n当前版本v0.7.3(Nonebot 2.0.0b1)")
    msg = f"来啦！\n系统信息如下：\nCPU占用：{str(per_cpu_status()[0])}%\n内存占用：{str(memory_status())}%\n"
    await ping.finish(msg + times)
