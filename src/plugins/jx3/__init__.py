from nonebot import get_driver

try:
    from .special_application import * # 公共实例独有功能，闭源
except:
    pass
from .jx3 import *

driver = get_driver()

@driver.on_startup
async def _():
    logger.info("Connecting to JX3API...Please wait.")
    await ws_client.init()
    logger.info("Connected to JX3API successfully.")

    logger.info("Connecting to SFAPI...Please wait.")
    await sf_ws_client.init()
    logger.info("Connected to SFAPI successfully.")

ws_recev = on(type="WsRecv", priority=5, block=False)
@ws_recev.handle()
async def _(bot: Bot, event: RecvEvent):
    message = event.get_message()
    if message == "False":
        return
    groups = await bot.call_api("get_group_list")
    for i in groups:
        group = i["group_id"]
        subscribe = load_or_write_subscribe(group)
        if message["type"] in subscribe:
            if message["type"] == "玄晶":
                group_info = json.loads(read(DATA + "/" + str(group) + "/jx3group.json"))
                if group_info["server"] != message["server"] and group_info["server"] != "":
                    continue
            elif message["type"] == "开服":
                group_info = json.loads(read(DATA + "/" + str(group) + "/jx3group.json"))
                if group_info["server"] != message["server"] and group_info["server"] != "":
                    continue
                elif group_info["server"] == "":
                    continue
            elif message["type"] == "818":
                group_info = json.loads(read(DATA + "/" + str(group) + "/jx3group.json"))
                if group_info["server"] != "" and group_info["server"] != message["server"] and message["name"] != "剑网3":
                    continue
            try:
                await bot.call_api("send_group_msg", group_id = group, message = message["msg"])
            except:
                logger.info(f"向群({i})推送失败，可能是因为风控、禁言或者未加入该群。")