"""仅转换文字与图片；不把 CQ 码或不支持的消息段发送给官方接口。"""

import base64
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import url2pathname

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.adapters.qq import Message as QQMessage, MessageSegment as QQSegment


def incoming_message(message: QQMessage) -> Message:
    result = Message()
    for segment in message:
        if segment.type == "text":
            result.append(MessageSegment.text(segment.data["text"]))
        elif segment.type == "image":
            url = str(segment.data["url"])
            if url.startswith("//"):
                url = "https:" + url
            if urlsplit(url).scheme in {"http", "https"}:
                result.append(MessageSegment.image(url))
    return result


def image_segment(source: str) -> QQSegment:
    if source.startswith("base64://"):
        return QQSegment.file_image(base64.b64decode(source[9:], validate = True))
    parsed = urlsplit(source)
    if parsed.scheme in {"http", "https"}:
        return QQSegment.image(source)
    if parsed.scheme == "file":
        if parsed.netloc not in {"", "localhost"}:
            raise ValueError("不支持远程 file URI 图片")
        return QQSegment.file_image(Path(url2pathname(parsed.path)))
    # OneBot 也允许普通的本地路径，兼容 Windows 盘符。
    return QQSegment.file_image(Path(source))


def outgoing_messages(message: Message) -> list[QQMessage]:
    """QQ 一条富媒体消息仅取一张图，因此拆开发送，文字只发送一次。"""
    text = "".join(segment.data["text"] for segment in message if segment.type == "text")
    images = [image_segment(str(segment.data["file"])) for segment in message if segment.type == "image"]
    if not images:
        return [QQMessage(QQSegment.text(text))] if text.strip() else []
    results = [QQMessage(image) for image in images]
    if text.strip():
        results[0].insert(0, QQSegment.text(text))
    return results
