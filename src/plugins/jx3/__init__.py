from nonebot import get_driver
from nonebot.log import logger

from src.config import Config
from src.const.path import ASSETS, build_path
from src.utils.generate import (
    ScreenshotGenerator
)
from src.utils.time import Time
from src.utils.database import cache_db
from src.utils.database.classes import JX3APIWSData
from src.utils.database.operation import send_subscribe
from src.plugins.jx3.announce.image import get_image as get_announce_image
from src.utils.database.attributes import TabCache

from .parse import (
    get_registered_actions,
    parse_data,
    JX3APIOutputMsg
)
from .weibo import poll_weibo_api
from .universe import * # 要不你来一个一个导？  # noqa: F403

import re
import asyncio
import websockets
import json
import os

driver = get_driver()

async def websocket_client(ws_url: str, headers: dict):
    if not Config.jx3.ws.enable:
        return
    while True:
        try:
            async with websockets.connect(ws_url, extra_headers=headers) as websocket:
                logger.info("WebSocket connection established")
                while True:
                    response_text = await websocket.recv()
                    raw_response = response_text
                    response: dict = json.loads(response_text)
                    if response["action"] not in get_registered_actions():
                        logger.warning("未知JX3API 消息: " + str(raw_response))
                        continue
                    logger.info("JX3API 解析成功: " + str(raw_response))
                    parsed = parse_data(response)
                    msg: JX3APIOutputMsg = parsed.msg()
                    cache_db.save(
                        JX3APIWSData(
                            action = response["action"],
                            event = msg.name,
                            data = response["data"],
                            timestamp = Time().raw_time
                        )
                    )
                    name = msg.name
                    if name == "公告":
                        url, title = parsed.provide_data()
                        if re.match(r"(\d+)月(\d+)日(.*?)版本更新公告", title):
                            if os.path.exists(build_path(ASSETS, ["image", "jx3", "update.png"])):
                                os.remove(build_path(ASSETS, ["image", "jx3", "update.png"]))
                            await get_announce_image()
                    await send_subscribe(name, msg.msg, msg.server)
                    logger.info(msg.msg)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed, retrying...")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        await asyncio.sleep(3)

def read_tab(tab_path: str) -> list[list]:
    with open(tab_path, encoding="gbk", mode="r") as f:
        return [a.strip().split("\t") for a in f.read().strip().split("\n")]

@driver.on_startup
async def on_startup():
    ws_url = Config.jx3.ws.url
    headers = {
        "token": Config.jx3.ws.token
    }
    TabCache.Attrib = read_tab(ASSETS + "/source/jx3/tabs/Attrib.tab")
    TabCache.Custom_Armor = read_tab(ASSETS + "/source/jx3/tabs/Custom_Armor.tab")
    TabCache.Custom_Trinket = read_tab(ASSETS + "/source/jx3/tabs/Custom_Trinket.tab")
    TabCache.Custom_Weapon = read_tab(ASSETS + "/source/jx3/tabs/Custom_Weapon.tab")
    TabCache.Enchant = read_tab(ASSETS + "/source/jx3/tabs/Enchant.tab")
    TabCache.Set = read_tab(ASSETS + "/source/jx3/tabs/Set.tab")
    TabCache.Item = read_tab(ASSETS + "/source/jx3/tabs/Item.txt")
    TabCache.Other = read_tab(ASSETS + "/source/jx3/tabs/Other.tab")
    TabCache.skill = read_tab(ASSETS + "/source/jx3/tabs/Skill.txt")
    TabCache.skillevent = read_tab(ASSETS + "/source/jx3/tabs/skillevent.txt")
    asyncio.create_task(websocket_client(ws_url, headers))
    asyncio.create_task(ScreenshotGenerator.launch())
    if Config.jx3.api.weibo:
        asyncio.create_task(poll_weibo_api("2046281757", interval=600))