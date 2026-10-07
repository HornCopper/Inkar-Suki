import asyncio
import base64

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment, PrivateMessageEvent
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.params import CommandArg

from src.utils.command import on_command

from .app import generate_image, information


castbar_matcher = on_command(
    'jx3_castbar', command_key='读条', aliases={'读条', '读条生成'},
    priority=5, force_whitespace=True,
)


@castbar_matcher.handle()
async def _(
    bot: Bot,
    event: GroupMessageEvent | PrivateMessageEvent,
    args: Message = CommandArg(),
):
    text = args.extract_plain_text().strip()
    try:
        help_text = await asyncio.to_thread(information, text)
        image = None if help_text is not None else await asyncio.to_thread(generate_image, text)
    except ValueError as error:
        await castbar_matcher.finish(str(error))
    except Exception:
        logger.exception('读条图片生成失败')
        await castbar_matcher.finish('读条图片生成失败，请稍后重试。')
    if help_text is not None:
        await castbar_matcher.finish(help_text)
    if image.format == 'apng':
        # NapCat file actions preserve APNG bytes; sending it as an image can
        # cause the chat client to replace the animation with a static preview.
        file = 'base64://' + base64.b64encode(image.content).decode('ascii')
        try:
            if isinstance(event, GroupMessageEvent):
                await bot.call_api('upload_group_file', group_id=event.group_id, file=file, name=image.filename)
            else:
                await bot.call_api('upload_private_file', user_id=event.user_id, file=file, name=image.filename)
        except ActionFailed:
            logger.exception('读条 APNG 文件发送失败')
            await castbar_matcher.finish('APNG 已生成，但文件发送失败。请检查群文件权限，或使用“格式=gif”生成聊天动图。')
        await castbar_matcher.finish('APNG 动图 PNG 已作为文件发送。')
    try:
        await castbar_matcher.finish(MessageSegment.image(image.content))
    except ActionFailed:
        logger.exception('读条图片发送失败')
        await castbar_matcher.finish('读条图片已生成，但图片发送失败，请稍后重试。')
