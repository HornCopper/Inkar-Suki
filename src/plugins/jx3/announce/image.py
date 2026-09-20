import asyncio
import base64
import hashlib
import os
from pathlib import Path
import time
from urllib.parse import urlparse

from nonebot.adapters.onebot.v11 import MessageSegment

from src.const.path import ASSETS, CACHE, build_path
from src.utils.network import Request
from src.utils.generate import generate

MOBILE_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/129.0.0.0 Mobile Safari/537.36"
)
PROJECT_FONT_PATH = Path(build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"]))
PUSH_IMAGE_CACHE = Path(build_path(CACHE, ["jx3", "announce_push"]))
PUSH_IMAGE_CACHE_VERSION = "wide-800-fixed-content-v5"
PUSH_IMAGE_WAIT_TIMEOUT = 180
PUSH_IMAGE_LOCK_STALE_AFTER = 600
PUSH_IMAGE_FAILURE_COOLDOWN = 300
BETA_PUSH_COALESCE_SECONDS = 30

prefix_html_code = """
<html>
<div style="width:770px;padding-left:40px;padding-right:40px;padding-top:80px">
<style>
    @font-face {
        font-family: Harmony;
        src: url("font_url");
    }

    body {
        font-family: Harmony, sans-serif !important;
    }
</style>
""".replace("font_url", PROJECT_FONT_PATH.as_uri())

async def get_image(ver: str = "latest"):
    raw_html = (await Request(f"https://jx3.xoyo.com/launcher/update/{ver}.html").get()).text
    html = _build_update_html(raw_html)
    return await generate(html.replace("font-family:微软雅黑;", ""), "div", True, segment=True)


def _build_update_html(raw_html: str) -> str:
    return prefix_html_code + raw_html + "</div></html>"


def _push_image_paths(url: str) -> tuple[Path, Path, Path]:
    cache_key = f"{PUSH_IMAGE_CACHE_VERSION}\0{url}"
    digest = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
    image_path = PUSH_IMAGE_CACHE / f"{digest}.png"
    return image_path, image_path.with_suffix(".lock"), image_path.with_suffix(".failed")


def _push_image_css() -> str:
    font = base64.b64encode(PROJECT_FONT_PATH.read_bytes()).decode("ascii")
    return f"""
        @font-face {{
            font-family: 'Inkar Suki';
            src: url('data:font/otf;base64,{font}') format('opentype');
            font-style: normal;
            font-weight: normal;
        }}
        html {{
            font-size: 50px !important;
        }}
        .article-wrapper {{
            width: 800px !important;
        }}
        .article-wrapper > [class*='articleRoot'],
        .article-wrapper .article-root {{
            width: 100% !important;
        }}
        .article-wrapper [class*='articleBox'],
        .article-wrapper [class*='mainContainer'],
        .article-wrapper [class*='articleContent'],
        .article-wrapper [class*='mainContainer'] > [class*='header'] {{
            width: 736px !important;
            max-width: none !important;
        }}
        .article-wrapper, .article-wrapper * {{
            font-family: 'Inkar Suki', sans-serif !important;
        }}
    """


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
        if time.time() - lock_path.stat().st_mtime > PUSH_IMAGE_LOCK_STALE_AFTER:
            lock_path.unlink()
    except FileNotFoundError:
        pass


def _has_recent_failure(failure_path: Path) -> bool:
    try:
        if time.time() - failure_path.stat().st_mtime <= PUSH_IMAGE_FAILURE_COOLDOWN:
            return True
        failure_path.unlink()
    except FileNotFoundError:
        pass
    return False


async def _ensure_cached_push_image(
    cache_key: str,
    render,
    is_usable=_has_complete_image,
) -> Path:
    """Render one shared screenshot across all Gunicorn worker processes."""
    image_path, lock_path, failure_path = _push_image_paths(cache_key)
    deadline = asyncio.get_running_loop().time() + PUSH_IMAGE_WAIT_TIMEOUT

    while not is_usable(image_path):
        if _has_recent_failure(failure_path):
            raise RuntimeError("Announcement screenshot generation recently failed")
        if _try_acquire_lock(lock_path):
            temporary_path = image_path.with_name(
                f"{image_path.stem}.{os.getpid()}.{time.time_ns()}.png"
            )
            try:
                if not is_usable(image_path):
                    await render(temporary_path)
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
            raise TimeoutError("Timed out waiting for the announcement screenshot")
        await asyncio.sleep(0.2)

    if not is_usable(image_path):
        raise RuntimeError("Announcement screenshot was not generated")
    return image_path


async def _ensure_push_image(url: str) -> Path:
    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or parsed_url.hostname != "jx3.xoyo.com":
        raise ValueError("Unsupported JX3 announcement URL")

    async def render(temporary_path: Path):
        await generate(
            url,
            ".article-wrapper",
            True,
            delay=1000,
            additional_css=_push_image_css(),
            additional_js="document.fonts.ready",
            viewport={"width": 800, "height": 900},
            output_path=str(temporary_path),
            wait_for_network=True,
            user_agent=MOBILE_USER_AGENT,
        )

    return await _ensure_cached_push_image(f"official:{url}", render)


async def _ensure_beta_push_image() -> Path:
    def is_recent(image_path: Path) -> bool:
        try:
            return (
                _has_complete_image(image_path)
                and time.time() - image_path.stat().st_mtime <= BETA_PUSH_COALESCE_SECONDS
            )
        except OSError:
            return False

    async def render(temporary_path: Path):
        raw_html = (
            await Request("https://jx3.xoyo.com/launcher/update/latest_exp.html").get()
        ).text
        html = _build_update_html(raw_html)
        await generate(
            html.replace("font-family:微软雅黑;", ""),
            "div",
            True,
            output_path=str(temporary_path),
        )

    return await _ensure_cached_push_image("beta:latest_exp", render, is_recent)


async def get_push_image(url: str) -> MessageSegment:
    image_path = await _ensure_push_image(url)
    image = await asyncio.to_thread(image_path.read_bytes)
    return MessageSegment.image(image)


async def get_beta_push_image() -> MessageSegment:
    image_path = await _ensure_beta_push_image()
    image = await asyncio.to_thread(image_path.read_bytes)
    return MessageSegment.image(image)
