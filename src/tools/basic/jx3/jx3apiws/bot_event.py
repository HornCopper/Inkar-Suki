from .events import *

from nonebot import get_bots
from nonebot.message import handle_event

import json


class BotEventController:
    @staticmethod
    async def raise_notice(message: str):
        """
        说明:
            抛出ws通知事件给机器人
        参数:
            * `message`：通知内容
        """
        event = WsNotice(message=message)
        bots = get_bots()
        for _, one_bot in bots.items():
            await handle_event(one_bot, event)

    @staticmethod
    async def handle_msg(message: str):
        """
        说明:
            处理收到的ws数据，分发给机器人
        """
        try:
            if isinstance(message, str):
                ws_obj = json.loads(message)
                data = WsData.parse_obj(ws_obj)
                event = EventRister.get_event(data)
            else:
                event:RecvEvent = message

            if event:
                logger.debug(f"ws-event:{event.log}")
                bots = get_bots()
                for _, one_bot in bots.items():
                    await handle_event(one_bot, event)
                    break
            else:
                logger.error(f"<r>未知的ws消息类型：{data}</r>")
        except Exception:
            logger.error(f"未知ws消息：<g>{ws_obj}</g>")