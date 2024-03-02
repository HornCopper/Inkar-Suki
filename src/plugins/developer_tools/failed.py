from nonebot.message import run_postprocessor

from src.tools.basic import *

@run_postprocessor
async def _(bot: Bot, event: Event, matcher: Matcher, exception: Optional[Exception]):
    if exception:
        for i in Config.owner:
            await bot.send_private_msg(user_id=int(i), message="群消息发送失败，账号可能被判定业务违规，请解除验证码！")