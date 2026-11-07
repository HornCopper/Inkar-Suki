"""为 QQ 号码和已记录的官方用户身份读取小头像，失败时交由界面降级。"""

import asyncio
import base64
from collections import OrderedDict
from io import BytesIO
import time
from typing import Iterable

import httpx
from PIL import Image, UnidentifiedImageError

from src.utils.identity import get_identity_store

_cache: OrderedDict[str, tuple[float, str | None]] = OrderedDict()
_CACHE_LIMIT = 256


def user_avatar_url(user_id: int | str) -> str | None:
    value = int(user_id)
    if value > 0:
        return f"https://q.qlogo.cn/headimg_dl?dst_uin={value}&spec=100"
    return get_identity_store().user_avatar_url(value) if value < 0 else None


async def load_user_avatars(user_ids: Iterable[int | str]) -> dict[str, str]:
    """头像预先嵌入图片，截图不再等待外网；每个进程缓存一小时。"""
    result: dict[str, str] = {}
    pending: dict[str, str] = {}
    now = time.monotonic()
    for identity in dict.fromkeys(str(value) for value in user_ids):
        url = user_avatar_url(identity)
        if not url:
            continue
        cached = _cache.get(url)
        if cached and cached[0] > now:
            _cache.move_to_end(url)
            if cached[1]:
                result[identity] = cached[1]
        else:
            pending[identity] = url
    if not pending:
        return result

    semaphore = asyncio.Semaphore(6)
    async with httpx.AsyncClient(timeout = 3, trust_env = False) as client:
        async def fetch(identity: str, url: str) -> None:
            avatar = None
            async with semaphore:
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    content = response.content
                    if len(content) <= 512 * 1024:
                        with Image.open(BytesIO(content)) as image:
                            mime = {"JPEG": "image/jpeg", "PNG": "image/png", "GIF": "image/gif", "WEBP": "image/webp"}.get(image.format)
                            image.verify()
                        if mime:
                            avatar = f"data:{mime};base64," + base64.b64encode(content).decode("ascii")
                except (httpx.HTTPError, UnidentifiedImageError, OSError, ValueError, SyntaxError):
                    pass
            _cache[url] = (time.monotonic() + (3600 if avatar else 300), avatar)
            _cache.move_to_end(url)
            while len(_cache) > _CACHE_LIMIT:
                _cache.popitem(last = False)
            if avatar:
                result[identity] = avatar

        await asyncio.gather(*(fetch(identity, url) for identity, url in pending.items()))
    return result
