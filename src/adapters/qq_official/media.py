"""共用媒体上传；被动回复发送文件和大图时保留原消息上下文。"""

import asyncio
import base64
import hashlib
from pathlib import Path
from typing import Any, Protocol, TYPE_CHECKING
from urllib.parse import urlsplit
from urllib.request import url2pathname

from nonebot.adapters.qq.models import Media
from nonebot.adapters.qq import Bot as QQBot
from nonebot.drivers import Request

if TYPE_CHECKING:
    from . import QQCompatBot

DIRECT_UPLOAD_LIMIT = 5 * 1024 * 1024
MAX_UPLOAD_SIZE = 200 * 1024 * 1024


class UploadContext(Protocol):
    native: QQBot
    is_group: bool
    target: str


def file_source(value: Any) -> bytes | str:
    if isinstance(value, bytes):
        content = value
    elif isinstance(value, Path):
        if value.stat().st_size > MAX_UPLOAD_SIZE:
            raise ValueError("文件大小超过 QQ 官方上传上限 200MB")
        content = value.read_bytes()
    else:
        value = str(value)
        if value.startswith("base64://"):
            if len(value) > (MAX_UPLOAD_SIZE * 4 // 3) + 20:
                raise ValueError("文件大小超过 QQ 官方上传上限 200MB")
            content = base64.b64decode(value[9:], validate = True)
        elif urlsplit(value).scheme in {"http", "https"}:
            return value
        elif urlsplit(value).scheme == "file":
            parsed = urlsplit(value)
            if parsed.netloc not in {"", "localhost"}:
                raise ValueError("不支持远程 file URI")
            return file_source(Path(url2pathname(parsed.path)))
        else:
            return file_source(Path(value))
    if len(content) > MAX_UPLOAD_SIZE:
        raise ValueError("文件大小超过 QQ 官方上传上限 200MB")
    return content


async def upload(bot: UploadContext, source: bytes | str, name: str, file_type: int) -> str:
    native = bot.native
    source = file_source(source)
    name = str(name).replace("\\", "/").rsplit("/", 1)[-1] or "file.bin"
    # SDK 1.7.3 的小文件上传未传 file_name，大文件合并也未保留 srv_send_msg=False。
    # 在兼容层补齐这两个字段，避免文件改名、重复发送或误占主动消息配额。
    if isinstance(source, bytes) and len(source) > DIRECT_UPLOAD_LIMIT:
        prepare_method = native.post_group_upload_prepare if bot.is_group else native.post_c2c_upload_prepare
        target = {"group_openid" if bot.is_group else "openid": bot.target}
        prepare = await prepare_method(
            **target, file_type = file_type, file_name = name, file_size = len(source),
            md5 = hashlib.md5(source).hexdigest(), sha1 = hashlib.sha1(source).hexdigest(),
            md5_10m = hashlib.md5(source[:10 * 1024 * 1024]).hexdigest(),
        )
        semaphore = asyncio.Semaphore(max(1, min(prepare.upload_config.concurrency, 8)))
        part_method = native._group_upload_part if bot.is_group else native._c2c_upload_part
        tasks = [asyncio.create_task(part_method(
            bot.target, prepare.upload_id, part.index, part.presigned_url,
            source[index * prepare.block_size:(index + 1) * prepare.block_size], semaphore,
        )) for index, part in enumerate(prepare.parts)]
        try:
            await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions = True)
        payload = {"upload_id": prepare.upload_id, "srv_send_msg": False}
    else:
        payload = {"file_type": file_type, "file_name": name, "srv_send_msg": False}
        if isinstance(source, bytes):
            payload["file_data"] = base64.b64encode(source).decode("ascii")
        else:
            payload["url"] = source
    route = "groups" if bot.is_group else "users"
    result = await native._request(Request(
        "POST", native.adapter.get_api_base().joinpath("v2", route, bot.target, "files"), json = payload,
    ))
    if not result.get("file_info"):
        raise ValueError("QQ 官方上传未返回可发送的文件信息")
    return result["file_info"]


async def send_media(bot: "QQCompatBot", source: bytes | str, name: str, file_type: int, content: str, sequence: int) -> Any:
    file_info = await upload(bot, source, name, file_type)
    # 上传可能耗时较长，发送前重新检查被动回复是否已过期。
    bot.ensure_reply_available(check_count = False)
    method = bot.native.post_group_messages if bot.is_group else bot.native.post_c2c_messages
    return await method(**{
        "group_openid" if bot.is_group else "openid": bot.target,
        "msg_type": 7, "media": Media(file_info = file_info), "content": content,
        "msg_id": bot.source.id, "msg_seq": sequence,
    })
