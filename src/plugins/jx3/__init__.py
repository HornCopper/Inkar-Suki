try:
    from .special_application import * # 公共实例独有功能，闭源
except:
    pass
from .jx3 import *
from nonebot import get_driver

driver = get_driver()

@driver.on_startup
async def _():
    logger.info("Connecting to JX3API...Please wait.")
    await ws_client.init()
    logger.info("Connected to JX3API successfully.")

ws_recev = on(type="WsRecv", priority=5, block=False)
@ws_recev.handle()
async def on_ws_recev(bot: Bot, event: RecvEvent):
    message = event.user_message_type
    if not message:
        return
    groups = await bot.call_api("get_group_list")
    for i in groups:
        group = i["group_id"]
        subscribe = json.loads(read(f"{DATA}{os.sep}{group}{os.sep}subscribe.json"))
        if message in subscribe:
            to_send_messagee = event.render_message(group)
            if not to_send_messagee:
                return # 无消息发送则退出
            try:
                await bot.call_api("send_group_msg", group_id = group, message = to_send_messagee)
            except:
                logger.info(f"向群({i})推送失败，可能是因为风控、禁言或者未加入该群。")