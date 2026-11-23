"""将当前官方群消息的文件附件转换为 OneBot 群文件上传通知。"""

from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from nonebot.adapters.onebot.v11 import GroupUploadNoticeEvent
from nonebot.adapters.qq.models.qq import Attachment

if TYPE_CHECKING:
    from . import QQCompatBot


def is_file_attachment(attachment: Attachment) -> bool:
    content_type = attachment.content_type.lower().split(";", 1)[0].strip()
    return content_type == "file" or content_type.startswith(("application/", "text/"))


def incoming_uploads(bot: "QQCompatBot") -> list[GroupUploadNoticeEvent]:
    if not bot.is_group:
        return []
    events = []
    for index, attachment in enumerate(bot.source.attachments or []):
        if not is_file_attachment(attachment):
            continue
        url = attachment.url or ""
        if url.startswith("//"):
            url = "https:" + url
        try:
            parsed = urlsplit(url)
            valid_url = parsed.scheme in {"http", "https"} and bool(parsed.hostname)
        except ValueError:
            valid_url = False
        if not valid_url:
            bot.log_compatibility("文件附件地址不是有效的 HTTP/HTTPS 地址", action = "省略入站文件")
            continue
        if not attachment.filename or attachment.size is None or attachment.size < 0:
            bot.log_compatibility("文件附件缺少文件名或有效大小", action = "省略入站文件")
            continue
        events.append(GroupUploadNoticeEvent(
            time = int(bot.timestamp), self_id = int(bot.self_id), post_type = "notice", notice_type = "group_upload",
            group_id = bot.group_id, user_id = bot.user_id, qq_official = True,
            # 官方没有 OneBot 文件 ID/busid；合成 ID 只在当前消息上下文中解析。
            file = {"id": f"{bot.source.id}:{index}", "name": attachment.filename, "size": attachment.size,
                    "busid": 0, "url": url},
        ))
    return events
