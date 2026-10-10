import base64

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment, PrivateMessageEvent
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.message import event_preprocessor
from nonebot.params import Arg, CommandArg
from nonebot.typing import T_State

from src.utils.command import on_command

from .app import generate_image_async
from .options import information, parse_request
from .renderer import IMAGE_PATH


ICON_PRESETS = {
    '五甲': IMAGE_PATH / 'preset_wujia.png',
    '无伤': IMAGE_PATH / 'preset_wushang.png',
}


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
    matcher: Matcher,
    state: T_State,
    args: Message = CommandArg(),
):
    text = args.extract_plain_text().strip()
    help_text = information(text)
    if help_text is not None:
        await achievement_tip_matcher.finish(help_text)
    try:
        state['achievement_request'] = parse_request(text)
    except ValueError as error:
        await achievement_tip_matcher.finish(str(error))
    if any(segment.type == 'image' for segment in args):
        matcher.set_arg('achievement_icon', args)


@achievement_tip_matcher.got(
    'achievement_icon',
    prompt='请发送一张图片作为成就图标，或回复以下文字：\n'
           '“头像”：使用你的 QQ 头像。\n'
           '【五甲】：使用五甲预设图标。\n'
           '【无伤】：使用无伤预设图标。\n'
           '发送其他内容则取消本次生成。',
)
async def generate_achievement_tip(
    bot: Bot,
    event: GroupMessageEvent | PrivateMessageEvent,
    state: T_State,
    icon: Message = Arg('achievement_icon'),
):
    has_image = any(segment.type == 'image' for segment in icon)
    choice = icon.extract_plain_text().strip() if all(segment.is_text() for segment in icon) else None
    if choice and choice.startswith('【') and choice.endswith('】'):
        choice = choice[1:-1]
    if not has_image and choice != '头像' and choice not in ICON_PRESETS:
        await achievement_tip_matcher.finish('已取消本次成就提示生成。')

    async def notify_queue(ahead: int):
        try:
            await achievement_tip_matcher.send(f'成就提示生成已排队，前面还有 {ahead} 个任务，完成后自动发送。')
        except ActionFailed:
            logger.exception('成就提示排队消息发送失败')

    try:
        request = state['achievement_request']
        if has_image:
            source = await image_source(bot, icon)
        elif choice == '头像':
            source = f'https://q.qlogo.cn/headimg_dl?dst_uin={event.user_id}&spec=100&img_type=jpg'
        else:
            source = ICON_PRESETS[choice].read_bytes()
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
