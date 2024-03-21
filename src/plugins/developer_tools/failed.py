from nonebot.message import run_postprocessor
from nonebot.adapters import Bot

from src.tools.basic import *

@run_postprocessor
async def _(bot: Bot, event: Event, matcher: Matcher, exception: Optional[Exception]):
    if exception:
        for i in Config.owner:
            await bot.send_private_msg(user_id=int(i), message=f"音卡出现了报错：\n{exception}")

@Bot.on_calling_api
async def _(event: Event, matcher: Matcher):
    to_check = event.get_message().extract_plain_text()
    final_url = f"https://inkar-suki.codethink.cn/banword?word={to_check}"
    data = await get_api(final_url)
    if data["num"] > 0:
        matcher.stop_propagation()