import asyncio
import os
from pathlib import Path
import re
import time

from nonebot.adapters.onebot.v11 import MessageSegment

from src.const.path import CACHE, build_path
from src.utils.generate import generate


MOBILE_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Mobile Safari/537.36"
)
WEIBO_SCREENSHOT_CACHE = Path(build_path(CACHE, ["jx3", "weibo_push"]))
WEIBO_SCREENSHOT_CACHE_VERSION = "mobile-card-v1"
WEIBO_SCREENSHOT_WAIT_TIMEOUT = 180
WEIBO_SCREENSHOT_LOCK_STALE_AFTER = 300
WEIBO_SCREENSHOT_FAILURE_COOLDOWN = 300
WEIBO_POST_ID_PATTERN = re.compile(r"^\d+$")
WEIBO_SCREENSHOT_CSS = """
    html, body, #app, .lite-page-wrap {
        width: 800px !important;
        max-width: none !important;
        margin: 0 !important;
        background: #fff !important;
    }
    .card-wrap, .f-weibo {
        width: 800px !important;
        max-width: none !important;
        margin: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
    }
    .card-act, .m-toolbar, .lite-page-editor, .open-app, .m-tab-bar {
        display: none !important;
    }
"""
WEIBO_SCREENSHOT_READY_JS = """
    Promise.race([
        Promise.all(Array.from(document.images).map((image) => {
            if (image.complete) return Promise.resolve();
            return new Promise((resolve) => {
                image.addEventListener('load', resolve, { once: true });
                image.addEventListener('error', resolve, { once: true });
            });
        })),
        new Promise((resolve) => setTimeout(resolve, 5000))
    ])
"""


def _screenshot_paths(post_id: str) -> tuple[Path, Path, Path]:
    stem = f"{post_id}.{WEIBO_SCREENSHOT_CACHE_VERSION}"
    image_path = WEIBO_SCREENSHOT_CACHE / f"{stem}.png"
    return image_path, image_path.with_suffix(".lock"), image_path.with_suffix(".failed")


def _has_complete_image(image_path: Path) -> bool:
    try:
        return image_path.is_file() and image_path.stat().st_size > 0
    except OSError:
        return False


def _try_acquire_lock(lock_path: Path) -> bool:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    try:
        os.write(descriptor, f"{os.getpid()} {time.time()}".encode("ascii"))
    finally:
        os.close(descriptor)
    return True


def _remove_stale_lock(lock_path: Path) -> None:
    try:
        if time.time() - lock_path.stat().st_mtime > WEIBO_SCREENSHOT_LOCK_STALE_AFTER:
            lock_path.unlink()
    except FileNotFoundError:
        pass


def _has_recent_failure(failure_path: Path) -> bool:
    try:
        if time.time() - failure_path.stat().st_mtime <= WEIBO_SCREENSHOT_FAILURE_COOLDOWN:
            return True
        failure_path.unlink()
    except FileNotFoundError:
        pass
    return False


async def _render_post_card(post_id: str, output_path: Path) -> None:
    await generate(
        f"https://m.weibo.cn/detail/{post_id}",
        ".f-weibo",
        True,
        delay=5000,
        additional_css=WEIBO_SCREENSHOT_CSS,
        additional_js=WEIBO_SCREENSHOT_READY_JS,
        viewport={"width": 800, "height": 1000},
        output_path=str(output_path),
        wait_for_network=False,
        user_agent=MOBILE_USER_AGENT,
    )


async def _ensure_post_card(post_id: str) -> Path:
    if not WEIBO_POST_ID_PATTERN.fullmatch(post_id):
        raise ValueError("微博 post_id 格式无效")

    image_path, lock_path, failure_path = _screenshot_paths(post_id)
    deadline = asyncio.get_running_loop().time() + WEIBO_SCREENSHOT_WAIT_TIMEOUT

    while not _has_complete_image(image_path):
        if _has_recent_failure(failure_path):
            raise RuntimeError("微博卡片截图最近生成失败")
        if _try_acquire_lock(lock_path):
            temporary_path = image_path.with_name(
                f"{image_path.stem}.{os.getpid()}.{time.time_ns()}.png"
            )
            try:
                if not _has_complete_image(image_path):
                    await _render_post_card(post_id, temporary_path)
                    os.replace(temporary_path, image_path)
                    failure_path.unlink(missing_ok=True)
            except Exception:
                failure_path.touch()
                raise
            finally:
                temporary_path.unlink(missing_ok=True)
                lock_path.unlink(missing_ok=True)
            break

        _remove_stale_lock(lock_path)
        if asyncio.get_running_loop().time() >= deadline:
            raise TimeoutError("等待微博卡片截图超时")
        await asyncio.sleep(0.2)

    if not _has_complete_image(image_path):
        raise RuntimeError("微博卡片截图未生成")
    return image_path


async def get_weibo_push_image(post_id: str) -> MessageSegment:
    image_path = await _ensure_post_card(post_id)
    image = await asyncio.to_thread(image_path.read_bytes)
    return MessageSegment.image(image)
