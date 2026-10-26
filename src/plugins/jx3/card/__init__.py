from nonebot import get_driver
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment, PrivateMessageEvent
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.params import CommandArg

from src.utils.command import on_command

from .app import execute_async, shutdown_renderer


social_card_matcher = on_command(
    'jx3_social_card', command_key='社交名片', aliases={'社交名片'},
    priority=5, force_whitespace=True,
)


@social_card_matcher.handle()
async def _(
    event: GroupMessageEvent | PrivateMessageEvent,
    args: Message = CommandArg(),
):
    try:
        result = await execute_async(args.extract_plain_text().strip(), user_id=event.get_user_id())
    except ValueError as error:
        await social_card_matcher.finish(str(error))
    except Exception:
        logger.exception('社交名片生成失败')
        await social_card_matcher.finish('社交名片生成失败，请稍后重试。')
    message = Message(result.text + '\n' if result.text and result.image else result.text)
    if result.image:
        message += MessageSegment.image(result.image)
    try:
        await social_card_matcher.finish(message)
    except ActionFailed:
        logger.exception('社交名片发送失败')
        await social_card_matcher.finish('图片已生成，但发送失败，请稍后重试。')


get_driver().on_shutdown(shutdown_renderer)
