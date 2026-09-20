from __future__ import annotations

import base64
from dataclasses import dataclass
import time
from typing import Any
from urllib.parse import urlencode, urlparse

from src.config import Config
from src.utils.network import Request


MAX_IMAGE_BYTES = 16 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 180
DOWNLOAD_TTL_SECONDS = 24 * 60 * 60
PUBLIC_DOWNLOAD_URL = "https://inkar-suki.codethink.cn/download"


@dataclass(frozen=True, slots=True)
class PreparedPreview:
    image: bytes
    result_id: str


@dataclass(frozen=True, slots=True)
class PreparedDownload:
    link: str
    materials: bytes


class PindouServiceError(RuntimeError):
    pass


def _api_base_url() -> str:
    configured = str(Config.jx3.api.cqc_url or "").strip().rstrip("/")
    if not configured:
        raise PindouServiceError(
            "请先在 src/config/config.yml 中配置 jx3.api.cqc_url。"
        )
    if configured.endswith("/pindou/convert"):
        configured = configured[:-len("/pindou/convert")]
    return configured


def _error_detail(response: Any) -> str:
    try:
        body = response.json()
    except Exception:
        return response.text.strip()[:500] or f"HTTP {response.status_code}"
    if isinstance(body, dict):
        detail = body.get("detail") or body.get("message") or body.get("error")
        if detail:
            return str(detail)[:500]
    return str(body)[:500]


async def download_image(url: str) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise PindouServiceError("图片地址不是有效的 HTTP/HTTPS 地址。")

    try:
        response = await Request(url).get(timeout=30)
    except Exception as exc:
        raise PindouServiceError("下载图片时网络请求失败。") from exc
    if response.status_code >= 400:
        raise PindouServiceError(f"图片服务器返回 HTTP {response.status_code}。")

    content = response.content
    if not content:
        raise PindouServiceError("图片内容为空。")
    if len(content) > MAX_IMAGE_BYTES:
        raise PindouServiceError("图片超过 16 MiB 限制。")
    return content


async def convert_preview(
    image: bytes,
    filename: str,
    options: dict[str, Any],
) -> PreparedPreview:
    payload = {
        "imageBase64": base64.b64encode(image).decode("ascii"),
        "filename": filename,
        "options": options,
    }
    endpoint = f"{_api_base_url()}/pindou/prepare"
    try:
        response = await Request(endpoint, params=payload).post(timeout=DEFAULT_TIMEOUT_SECONDS)
    except Exception as exc:
        raise PindouServiceError("无法连接拼豆转换服务。") from exc
    if response.status_code >= 400:
        raise PindouServiceError(_error_detail(response))
    try:
        body = response.json()
        result_id = body["resultId"]
        encoded_preview = body["preview"]["imageBase64"]
        if not isinstance(result_id, str) or len(result_id) != 43:
            raise ValueError("resultId")
        if not isinstance(encoded_preview, str) or len(encoded_preview) > 24 * 1024 * 1024:
            raise ValueError("preview")
        preview = base64.b64decode(encoded_preview, validate=True)
        if not preview or len(preview) > MAX_IMAGE_BYTES:
            raise ValueError("preview")
    except (ValueError, KeyError, TypeError) as exc:
        raise PindouServiceError("转换服务返回了无效的预览结果。") from exc
    return PreparedPreview(image=preview, result_id=result_id)


async def create_download_link(result_id: str) -> PreparedDownload:
    """Publish the cached blueprint and retrieve its matching material sheet."""
    endpoint = f"{_api_base_url()}/pindou/download"
    try:
        response = await Request(
            endpoint,
            params={
                "resultId": result_id,
                "expires_at": int(time.time()) + DOWNLOAD_TTL_SECONDS,
            },
        ).post(timeout=60)
    except Exception as exc:
        raise PindouServiceError("无法连接下载服务，请稍后重试。") from exc
    if response.status_code >= 400:
        raise PindouServiceError(_error_detail(response))
    try:
        result = response.json()
        token = result.get("token") if isinstance(result, dict) else None
    except ValueError as exc:
        raise PindouServiceError("下载服务返回的内容无效。") from exc
    if not isinstance(token, str) or not token.strip():
        raise PindouServiceError("下载服务未返回有效 token。")
    try:
        materials = result["materials"]
        encoded = materials["imageBase64"]
        if materials["mediaType"] != "image/png" or not isinstance(encoded, str) or len(encoded) > 24 * 1024 * 1024:
            raise ValueError("materials")
        image = base64.b64decode(encoded, validate=True)
        if len(image) > MAX_IMAGE_BYTES or not image.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("materials image")
    except (ValueError, KeyError, TypeError) as exc:
        raise PindouServiceError("下载服务未返回有效的材料清单图片，请重新生成预览后重试。") from exc
    return PreparedDownload(
        link=f"{PUBLIC_DOWNLOAD_URL}?{urlencode({'token': token})}",
        materials=image,
    )

