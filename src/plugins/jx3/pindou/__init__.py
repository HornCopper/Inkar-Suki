from __future__ import annotations

from nonebot import on_message
from nonebot.adapters.onebot.v11 import Message, MessageEvent, GroupMessageEvent, MessageSegment as ms
from nonebot.matcher import Matcher
from nonebot.params import Arg, CommandArg
from nonebot.rule import Rule
from nonebot.typing import T_State

from src.utils.command import on_command

from .client import PindouServiceError, convert_preview, create_download_link, download_image
from .options import PARAMETER_PROMPT, PindouOptionError, parse_options
from src.const.prompts import PROMPT
from .sources import get_card_image_url, resolve_card_server

jiayuanpindou_matcher = on_command("jx3_pindou", command_key="拼豆", aliases={"家园拼豆"}, force_whitespace=True, priority=5)


@jiayuanpindou_matcher.handle()
async def _(event: GroupMessageEvent, message: Message = CommandArg()):
    if message.extract_plain_text().strip():
        await jiayuanpindou_matcher.finish("参考格式：家园拼豆")
    await jiayuanpindou_matcher.finish("图片转化家园拼豆蓝图网址：\nhttps://txjydps.online/pindou2jx3/")


TRIGGER = "拼豆蓝图"
ACTION_PROMPT = (
    "回复“下载链接”获取家园蓝图文件；\n"
    "回复“调整参数”修改蓝图转换参数；\n"
    "回复其他内容停止本次蓝图转换。\n\n回复“家园拼豆”获取拼豆网址，可以体验更多特性！"
)
IMAGE_PROMPT = "请发送一张图片，收到后将按默认参数转换拼豆蓝图。回复“取消”退出。\n请注意不要发送太快，若发送图片后未产生提示，请等待3秒左右再次发送。"
CARD_USAGE = "格式：拼豆蓝图 名片 服务器 角色名\n例如：拼豆蓝图 名片 华乾 谢焚卿"


async def _is_pindou_request(event: MessageEvent) -> bool:
    message = event.get_message()
    return TRIGGER in message.extract_plain_text()


def _first_image(message: Message):
    return next(
        (segment for segment in message if segment.type == "image"),
        None,
    )


def _safe_filename(raw_name: object) -> str:
    filename = str(raw_name or "image.png").replace("\\", "/").rsplit("/", 1)[-1]
    filename = filename.strip()[:255]
    return filename or "image.png"


pindou_matcher = on_message(
    rule=Rule(_is_pindou_request),
    priority=5,
    block=True,
)


async def _show_preview(state: T_State, options: dict):
    preview = await convert_preview(
        state["pindou_image"],
        state["pindou_filename"],
        options,
    )
    await pindou_matcher.send(ms.image(preview.image))
    state["pindou_result_id"] = preview.result_id
    state["pindou_options_dict"] = options
    state["pindou_stage"] = "action"


async def _generate_initial_preview(image_segment: ms, state: T_State):
    image_url = str(
        image_segment.data.get("url")
        or (
            image_segment.data.get("file")
            if str(image_segment.data.get("file") or "").startswith(("http://", "https://"))
            else ""
        )
    )
    if not image_url:
        await pindou_matcher.finish("无法取得这张图片的下载地址，请重新发送原图后再试。")

    try:
        image_bytes = await download_image(image_url)
    except PindouServiceError as exc:
        await pindou_matcher.finish(f"读取图片失败：{exc}")
    except Exception:
        await pindou_matcher.finish("读取图片失败，已结束本次拼豆转换，请稍后重试。")

    state["pindou_image"] = image_bytes
    state["pindou_filename"] = _safe_filename(image_segment.data.get("file"))
    await pindou_matcher.send("正在按默认参数转换预览图，请稍候……\n图片转换过程中未使用 AI 美术，请放心使用。")
    try:
        await _show_preview(state, parse_options("默认"))
    except PindouServiceError as exc:
        await pindou_matcher.finish(f"转换预览图失败：{exc}")


@pindou_matcher.handle()
async def start_pindou(event: MessageEvent, state: T_State):
    source_args = event.get_message().extract_plain_text().partition(TRIGGER)[2].split()
    if source_args:
        if source_args[0] != "名片":
            await pindou_matcher.finish(f"图片来源暂时只支持“名片”。\n{CARD_USAGE}")
        if len(source_args) != 3:
            await pindou_matcher.finish(f"{PROMPT.ArgumentCountInvalid}\n{CARD_USAGE}")
        _, server, role_name = source_args
        try:
            server = resolve_card_server(server)
        except PindouServiceError as exc:
            await pindou_matcher.finish(str(exc))
        await pindou_matcher.send(f"正在查询 [{role_name}·{server}] 的名片，请稍候……")
        try:
            image_url = await get_card_image_url(server, role_name)
        except PindouServiceError as exc:
            await pindou_matcher.finish(str(exc))
        image_segment = ms("image", {"url": image_url, "file": f"{role_name}名片.png"})
        await _generate_initial_preview(image_segment, state)
        await pindou_matcher.send(ACTION_PROMPT)
        return

    image_segment = _first_image(event.get_message())
    if image_segment is None:
        state["pindou_stage"] = "image"
        await pindou_matcher.send(IMAGE_PROMPT)
        return

    await _generate_initial_preview(image_segment, state)
    await pindou_matcher.send(ACTION_PROMPT)


@pindou_matcher.got("pindou_reply")
async def handle_pindou_reply(
    state: T_State,
    matcher: Matcher,
    pindou_reply: Message = Arg(),
):
    answer = pindou_reply.extract_plain_text().strip().lower()
    if answer in {"取消", "cancel", "否", "不", "no", "n"}:
        await pindou_matcher.finish("已结束本次拼豆转换。")

    if state.get("pindou_stage") == "image":
        image_segment = _first_image(pindou_reply)
        if image_segment is None:
            await pindou_matcher.finish("未收到图片，已结束本次拼豆转换。需要时请重新发送命令。")
        await _generate_initial_preview(image_segment, state)
        await matcher.reject(ACTION_PROMPT)

    image = state.get("pindou_image")
    options = state.get("pindou_options_dict")
    if not isinstance(image, bytes) or not isinstance(options, dict):
        await pindou_matcher.finish("图片会话已失效，请重新发送图片和触发词。")

    if state.get("pindou_stage") == "parameters":
        try:
            updated_options = parse_options(answer)
        except PindouOptionError as exc:
            await matcher.reject(f"参数有误：{exc}\n请重新输入，或回复“取消”。")

        await pindou_matcher.send("正在按新参数转换预览图，请稍候……")
        try:
            await _show_preview(state, updated_options)
        except PindouServiceError as exc:
            await matcher.reject(f"转换预览图失败：{exc}\n请重新输入参数，或回复“取消”。")
        # Repeat this handler for the next user message, now at the action stage.
        await matcher.reject(ACTION_PROMPT)

    if answer == "调整参数":
        state["pindou_stage"] = "parameters"
        await matcher.reject(PARAMETER_PROMPT)
    if answer != "下载链接":
        await pindou_matcher.finish("已停止本次蓝图转换。")

    result_id = state.get("pindou_result_id")
    if not isinstance(result_id, str) or not result_id:
        await matcher.reject(f"预览结果已失效，请选择“调整参数”重新转换。")
    await pindou_matcher.send("正在转换下载链接，请稍候……")
    try:
        download = await create_download_link(result_id)
    except PindouServiceError as exc:
        await matcher.reject(f"转换下载链接失败：{exc}\n{ACTION_PROMPT}")
    await pindou_matcher.finish(
        Message(f"家园拼豆蓝图下载链接（有效期24小时）：\n{download.link}\n\n材料清单：\n")
        + ms.image(download.materials)
    )
