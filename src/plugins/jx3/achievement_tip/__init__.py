import base64

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment, PrivateMessageEvent
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.message import event_preprocessor
from nonebot.params import CommandArg

from src.utils.command import on_command

from .app import generate_image_async
from .options import information, parse_request


achievement_tip_matcher = on_command(
    'jx3_achievement_tip', command_key='成就提示', aliases={'成就提示', '成就条'},
    priority=5, force_whitespace=True,
)


@event_preprocessor
async def normalize_image_command(event: GroupMessageEvent | PrivateMessageEvent):
    """Let an attached icon precede this command's text in the same message."""
    message = event.get_message()
    if not message or message[0].type != 'image':
        return
    offset = 0
    while offset < len(message) and message[offset].type == 'image':
        offset += 1
    if offset == len(message) or not message[offset].is_text():
        return
    text = str(message[offset]).lstrip()
    names = {'成就提示', '成就条', 'jx3_achievement_tip'}
    starts = get_driver().config.command_start
    def matches(prefix):
        return text.startswith(prefix) and (len(text) == len(prefix) or text[len(prefix)].isspace())

    if any(matches(start + name) for start in starts for name in names):
        event.message = Message(message[offset:]) + Message(message[:offset])


async def image_source(bot: Bot, message: Message) -> str | None:
    images = [segment for segment in message if segment.type == 'image']
    if len(images) > 1:
        raise ValueError('请在同一条命令中只附一张图标图片。')
    if not images:
        return None
    image = images[0]
    for field in ['url', 'file']:
        value = str(image.data.get(field) or '')
        if value.startswith(('http://', 'https://', 'base64://')):
            return value
    file = image.data.get('file')
    if file:
        try:
            data = await bot.call_api('get_image', file=file)
        except ActionFailed:
            raise ValueError('无法取得图标图片，请重新发送原图。') from None
        if not isinstance(data, dict):
            raise ValueError('无法取得图标图片，请重新发送原图。')
        for field in ['url', 'file']:
            value = str(data.get(field) or '')
            if value.startswith(('http://', 'https://', 'base64://')):
                return value
    raise ValueError('无法取得图标的下载地址，请重新发送原图。')


@achievement_tip_matcher.handle()
async def handle_achievement_tip(
    bot: Bot,
    event: GroupMessageEvent | PrivateMessageEvent,
    args: Message = CommandArg(),
):
    text = args.extract_plain_text().strip()
    help_text = information(text)
    if help_text is not None:
        await achievement_tip_matcher.finish(help_text)

    async def notify_queue(ahead: int):
        try:
            await achievement_tip_matcher.send(f'成就提示生成已排队，前面还有 {ahead} 个任务，完成后自动发送。')
        except ActionFailed:
            logger.exception('成就提示排队消息发送失败')

    try:
        request = parse_request(text)
        source = await image_source(bot, args)
        image = await generate_image_async(request, source, notify_queue)
    except ValueError as error:
        await achievement_tip_matcher.finish(str(error))
    except Exception:
        logger.exception('成就提示生成失败')
        await achievement_tip_matcher.finish('成就提示生成失败，请稍后重试。')

    if image.format == 'apng':
        file = 'base64://' + base64.b64encode(image.content).decode('ascii')
        try:
            if isinstance(event, GroupMessageEvent):
                await bot.call_api('upload_group_file', group_id=event.group_id, file=file, name=image.filename)
            else:
                await bot.call_api('upload_private_file', user_id=event.user_id, file=file, name=image.filename)
        except ActionFailed:
            logger.exception('成就提示 APNG 文件发送失败')
            await achievement_tip_matcher.finish('APNG 已生成，但文件发送失败。请检查文件权限，或使用“格式=gif”。')
        await achievement_tip_matcher.finish('APNG 已作为文件发送。')
    try:
        await achievement_tip_matcher.finish(MessageSegment.image(image.content))
    except ActionFailed:
        logger.exception('成就提示图片发送失败')
        await achievement_tip_matcher.finish('成就提示已生成，但图片发送失败，请稍后重试。')
