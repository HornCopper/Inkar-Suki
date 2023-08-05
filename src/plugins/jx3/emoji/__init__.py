from random import random

from src.tools.dep import *

rdemoji = on_command("jx3_emoji", aliases={"随机表情"}, priority=5)

@rdemoji.handle()
async def _(event: GroupMessageEvent):
    api = "https://cms.jx3box.com/api/cms/post/emotions?type=&search=&star=&original=&page=1&per=50"
    data = await get_api(api)
    data = data["data"]["list"]
    failed_time = 0
    while True:
        rdnum = random.randint(0, len(data) - 1)
        status = await get_status(data[rdnum]["url"])
        if status == 200:
            await rdemoji.finish(data[rdnum]["url"])
        else:
            failed_time = failed_time + 1
            if failed_time == 5:
                return await rdemoji.finish("唔……已经失败超过5次，查找失败！")
            continue