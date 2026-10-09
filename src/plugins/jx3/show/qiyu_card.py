from dataclasses import replace

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment as ms, PrivateMessageEvent
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.params import CommandArg

from src.const.jx3.server import Server
from src.utils.command import on_command
from .card_queue import SerialCardQueue
from .qiyu_card_app import generate_card, parse_arguments, shutdown_renderer


qiyu_card_matcher = on_command(
    'jx3_qiyu_card', command_key='奇遇名片', aliases={'奇遇名片'},
    force_whitespace=True, priority=5,
)
QUEUE = SerialCardQueue()


@qiyu_card_matcher.handle()
async def handle_qiyu_card(
    bot: Bot,
    event: GroupMessageEvent | PrivateMessageEvent,
    args: Message = CommandArg(),
):
    try:
        request = parse_arguments(args.extract_plain_text().strip())
        server = Server(request.server).server
        if not server:
            raise ValueError('无法识别服务器，请检查服务器名称。')
        request = replace(request, server=server)
    except ValueError as error:
        await qiyu_card_matcher.finish(str(error))

    async def process():
        try:
            image, placement = await generate_card(request)
            logger.debug(f'奇遇名片算法定位耗时 {placement.analysis_ms:.2f} ms，位置 ({placement.left}, {placement.top})')
            message = ms.image(image)
        except ValueError as error:
            logger.warning(f'奇遇名片未完成：{error}')
            message = str(error)
        except Exception:
            logger.exception('奇遇名片查询或生成失败')
            message = '奇遇名片生成失败，请稍后重试；后续排队任务会继续处理。'
        if isinstance(event, GroupMessageEvent):
            message = ms.at(event.user_id) + message
        # Sending belongs to the queued job, so results retain FIFO order.
        await bot.send(event, message)

    try:
        ticket = QUEUE.enqueue(process)
    except RuntimeError as error:
        await qiyu_card_matcher.finish(str(error))
    try:
        if ticket.ahead:
            await qiyu_card_matcher.send(f'奇遇名片已排队（#{ticket.number}），前面还有 {ticket.ahead} 个任务，完成后自动发送。')
    except ActionFailed:
        # A failed acknowledgement must not discard an accepted request.
        logger.exception('奇遇名片排队提示发送失败，继续处理任务')
    try:
        await QUEUE.wait(ticket)
    except ActionFailed:
        logger.exception('奇遇名片结果发送失败')
        await qiyu_card_matcher.finish('图片已生成，但发送失败，请稍后重试。')


@get_driver().on_shutdown
async def shutdown_qiyu_cards():
    await QUEUE.close()
    await shutdown_renderer()
