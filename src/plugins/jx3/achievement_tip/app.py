"""Bounded image downloads and sequential generation off the bot event loop."""
import asyncio
import base64
import binascii
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import threading

import httpx

from .options import TipRequest
from . import renderer


_RENDER_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix='achievement-tip')
_QUEUE_LOCK = threading.Lock()
_QUEUED_JOBS = []
MAX_QUEUED_JOBS = 8


@dataclass(frozen=True)
class GeneratedImage:
    content: bytes
    filename: str
    format: str


def download_icon(source: str | bytes) -> bytes:
    if isinstance(source, bytes):
        if len(source) > renderer.MAX_IMAGE_BYTES:
            raise ValueError('图标图片不能超过 8 MiB，请缩小后重新发送。')
        return source
    if source.startswith('base64://'):
        payload = source.removeprefix('base64://')
        if len(payload) > (renderer.MAX_IMAGE_BYTES + 2) // 3 * 4:
            raise ValueError('图标图片不能超过 8 MiB，请缩小后重新发送。')
        try:
            return download_icon(base64.b64decode(payload, validate=True))
        except (binascii.Error, ValueError):
            raise ValueError('图标图片数据无效，请重新发送原图。') from None
    if not source.startswith(('http://', 'https://')):
        raise ValueError('无法取得图标的下载地址，请重新发送原图。')
    try:
        with httpx.Client(follow_redirects=True, timeout=15) as client:
            with client.stream('GET', source) as response:
                response.raise_for_status()
                chunks = []
                size = 0
                for chunk in response.iter_bytes(chunk_size=65536):
                    size += len(chunk)
                    if size > renderer.MAX_IMAGE_BYTES:
                        raise ValueError('图标图片不能超过 8 MiB，请缩小后重新发送。')
                    chunks.append(chunk)
                return b''.join(chunks)
    except httpx.HTTPError:
        raise ValueError('图标下载失败，请重新发送原图后再试。') from None


def generate_image(request: TipRequest, image_source: str | bytes | None = None) -> GeneratedImage:
    icon = renderer.custom_icon(download_icon(image_source)) if image_source is not None else None
    content = renderer.render(request, icon)
    suffix = 'apng.png' if request.format == 'apng' else request.format
    return GeneratedImage(content, f'achievement_tip_806x276.{suffix}', request.format)


def _remove_finished_job(future):
    with _QUEUE_LOCK:
        _QUEUED_JOBS.remove(future)


async def generate_image_async(request: TipRequest, image_source=None, on_queued=None) -> GeneratedImage:
    # Download and rendering occupy the same worker, preserving request order
    # without letting image downloads block NoneBot's event loop.
    with _QUEUE_LOCK:
        ahead = sum(not job.done() for job in _QUEUED_JOBS)
        if ahead >= MAX_QUEUED_JOBS:
            raise ValueError('成就提示生成队列已满，请稍后再试。')
        future = _RENDER_EXECUTOR.submit(generate_image, request, image_source)
        _QUEUED_JOBS.append(future)
    future.add_done_callback(_remove_finished_job)
    pending = asyncio.wrap_future(future)
    try:
        if ahead and on_queued is not None:
            await on_queued(ahead)
        return await pending
    except BaseException:
        future.cancel()
        pending.cancel()
        raise
