import shutil

from nonebot import get_driver

from .jx3 import *

driver = get_driver()


@driver.on_startup
async def nonebot_on_startup():
    logger.info("nonebot_on_startup...")

    logger.debug("Connecting to JX3API...Please wait.")
    if await ws_client.init():
        logger.info("Connected to JX3API successfully.")

ws_recev = on(type="WsRecv", priority=5, block=False)


@ws_recev.handle()
async def on_jx3_event_recv(bot: Bot, event: RecvEvent):
    message = event.get_message()
    if message == "False":
        return
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
                await bot.call_api("send_group_msg", group_id=i, message=message["msg"])
            else:
                if getGroupData(str(i), "server") == message["server"]:
                    await bot.call_api("send_group_msg", group_id=i, message=message["msg"])