from nonebot.adapters import Bot

from src.tools.basic import *

@Bot.on_calling_api
async def _(event: Event, matcher: Matcher):
    to_check = event.get_message().extract_plain_text()
    final_url = f"https://inkar-suki.codethink.cn/banword?word={to_check}"
    data = await get_api(final_url)
    if data["num"] > 0:
        matcher.stop_propagation()