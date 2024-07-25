from nonebot import get_driver

from .jx3 import *

driver = get_driver()


@driver.on_startup
async def nonebot_on_startup():
    logger.info("nonebot_on_startup...")

    logger.debug("Connecting to JX3API...Please wait.")
    if await ws_client.init():
        logger.info("Connected to JX3API successfully.")

jx3api_ws = on(type="WsRecv", priority=5, block=False)

@jx3api_ws.handle()
async def _(event: RecvEvent):
    message = event.get_message()
    if not message or not message.get("type"):
        return
    bots = get_bots()  
    for bot_name, bot_instance in bots.items():
        bot_groups = await bot_instance.call_api("get_group_list")
        available_groups = [int(group["group_id"]) for group in bot_groups if str(group["group_id"]) in getAllGroups()]
        msg_type = message["type"]
        for group_id in available_groups:
            group_data = getGroupSettings(str(group_id))
            if msg_type not in getGroupSettings(str(group_id), "subscribe"):
                continue
            if "server" not in message:
                await bot_instance.call_api("send_group_msg", group_id=group_id, message=message["msg"])
                continue
            if group_data.get("server") == message.get("server"):
                if msg_type == "抓马" and "horse" in message:
                    horse_name = message["horse"]
                    if "抓马过滤" in group_data.get("addtions", []) and horse_name not in ["赤兔", "里飞沙"]:
                        continue
                if msg_type == "抓马" and "map" in message:
                    map_name = message["map"]
                    if "抓马过滤" in group_data.get("addtions", []) and map_name not in ["黑龙沼", "黑戈壁", "阴山大草原", "鲲鹏岛"]:
                        continue

                if msg_type == "奇遇" and "奇遇过滤" in group_data.get("addtions", []):
                    if message.get("level") != 2:
                        continue

                await bot_instance.call_api("send_group_msg", group_id=group_id, message=message["msg"])
            continue