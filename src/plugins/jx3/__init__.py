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

@ws_recev.handle()
async def _(event: RecvEvent):
    if event.get_message()["type"] == "开服":
        if datetime.date.today().weekday() + 1 == 1:
            await asyncio.sleep(900)
            shutil.rmtree(ASSETS + "/jx3/monsters.jpg")
        