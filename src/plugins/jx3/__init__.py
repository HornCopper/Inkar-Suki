from nonebot import get_driver

from .jx3 import *

import shutil
import datetime

driver = get_driver()


@driver.on_startup
async def nonebot_on_startup():
    logger.info("nonebot_on_startup...")

    logger.debug("Connecting to JX3API...Please wait.")
    if await ws_client.init():
        logger.info("Connected to JX3API successfully.")

jx3api_ws = on(type="WsRecv", priority=5, block=False)

@jx3api_ws.handle()
async def on_jx3_event_recv(bot: Bot, event: RecvEvent):
    message = event.get_message()
    if not message or message["type"] == "":
        return
    if message["type"] == "开服" and datetime.date.today().weekday() == 0:
        shutil.rmtree(ASSETS + "/jx3/monsters.jpg")
    logger.info(message["msg"])
    groups = os.listdir(DATA)
    available_group = []
    bot_groups = await bot.call_api("get_group_list")
    for i in bot_groups:
        if str(i["group_id"]) in groups:
            available_group.append(int(i["group_id"]))
    msg_type = message["type"]
    for i in available_group:
        if msg_type in getGroupData(str(i), "subscribe"):
            if "server" not in list(message):
                await bot.call_api("send_group_msg", group_id=i, message=message["msg"], whitelist=1)
                continue
            else:
                if getGroupData(str(i), "server") == message["server"]:
                    if "抓马过滤" in getGroupData(str(i), "addtions") and (message["msg"].find(" 赤兔 ") == -1 or message["msg"].find(" 里飞沙 ") == -1) and message["type"] == "抓马":
                        continue
                    await bot.call_api("send_group_msg", group_id=i, message=message["msg"], whitelist=1)
                    continue
                else:
                    continue