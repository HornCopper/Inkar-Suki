from nonebot.adapters import Bot
from nonebot.exception import MockApiException

from src.tools.basic import *

@Bot.on_calling_api
async def handle_api_call(bot: Bot, api: str, data: dict):
    if api == "send_group_msg":
        to_check = data["message"]
        logger.info("Checking message……")
        data = await get_api("https://inkar-suki.codethink.cn/banword?word=" + to_check)
        if data["code"] == 200:
            raise MockApiException("The content is not lawful!")