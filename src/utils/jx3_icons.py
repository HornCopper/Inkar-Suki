from hashlib import sha256
from typing import TYPE_CHECKING
from urllib.parse import quote, unquote, urlsplit

import re

if TYPE_CHECKING:
    from playwright.async_api import Route

JX3_ASSET_PATTERN = re.compile(
    r"^https?://(?:icon|img|cdn)\.jx3box\.com(?::[0-9]+)?/",
    re.IGNORECASE,
)
_UI_PREFIXES = {
    "img.jx3box.com": {
        "/image/camp/": "/image/camp/",
        "/image/box/": "/image/box/",
        "/pve/minimap/": "/image/minimap/",
    },
    "cdn.jx3box.com": {
        "/static/pz/img/overview/horizontal/": "/image/school_bg/",
        "/static/fonts/": "/static/fonts/",
    },
}

def _api_root(base_url: str | None = None) -> str:
    if base_url is None:
        from src.config import Config

        base_url = Config.jx3.api.calculator_url
    root = base_url.strip().rstrip("/")
    if not root:
        raise ValueError("请配置 jx3.api.calculator_url 以访问自管图标库。")
    return root

def icon_url(icon_id: object, base_url: str | None = None) -> str:
    value = str(icon_id).strip()
    value = str(int(value)) if re.fullmatch(r"[0-9]{1,10}", value) else "_missing"
    return f"{_api_root(base_url)}/icon/{value}.png"

def asset_url(source: str, base_url: str | None = None) -> str:
    """将原有 JX3BOX 图标和界面图片地址转换为自管接口地址。"""
    try:
        parsed = urlsplit(source)
        host = parsed.hostname
    except ValueError:
        return source
    if parsed.scheme not in {"http", "https"}:
        return source
    path = unquote(parsed.path)
    if host == "icon.jx3box.com":
        match = re.fullmatch(r"/icon/([0-9]+)\.png", path, re.IGNORECASE)
        return icon_url(match[1] if match else None, base_url)
    for prefix, target in _UI_PREFIXES.get(host or "", {}).items():
        if path.startswith(prefix):
            filename = path[len(prefix):]
            if not filename or filename in {".", ".."} or any(c in filename for c in "/\\\0:"):
                return icon_url(None, base_url)
            query = f"?{parsed.query}" if parsed.query else ""
            return f"{_api_root(base_url)}{target}{quote(filename, safe='')}{query}"
    return source

def asset_cache_name(url: str, base_url: str | None = None) -> str | None:
    """为自管图片单独生成缓存名，避免沿用旧 CDN 或其他站点的同名缓存。"""
    parsed = urlsplit(url)
    if base_url is None:
        from src.config import Config

        base_url = Config.jx3.api.calculator_url
    root = base_url.strip().rstrip("/")
    if not root:
        return None
    if not url.startswith(tuple(root + prefix for prefix in ("/icon/", "/image/", "/static/fonts/"))):
        return None
    filename = parsed.path.rsplit("/", 1)[-1]
    return f"jx3-{sha256(url.encode('utf-8')).hexdigest()[:16]}-{filename}"

async def serve_api_asset(route: "Route") -> None:
    """截图时从自管接口加载原页面引用的图片和字体。"""
    source = route.request.url
    target = asset_url(source)
    if target == source:
        await route.continue_()
    else:
        response = await route.fetch(url = target)
        await route.fulfill(response = response)
