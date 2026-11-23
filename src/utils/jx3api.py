"""Adapt JX3API's header authentication and status/detail response envelope."""

from typing import Any

from src.config import Config


async def jx3api_get(
    path: str,
    *,
    params: dict[str, Any] | None = None,
    timeout: int = 20,
) -> dict[str, Any]:
    """Return code/data/msg for existing consumers, including older API proxies.

    Tokens belong in the request header. Keep business payloads intact: a
    nested status/detail pair can be part of the endpoint's own data.
    """
    # Request imports decorators, so defer this import to avoid a cycle.
    from src.utils.network import Request

    query = dict(params or {})
    token = query.pop("token", None)
    if token is not None:
        token = str(token).strip() or Config.jx3.api.token.strip() or Config.jx3.api.token_v2.strip()
    headers = {"token": token} if token else {}
    if path.startswith(("https://", "http://")):
        url = path
    else:
        url = f"{Config.jx3.api.url.rstrip('/')}/{path.lstrip('/')}"
    response = await Request(url, headers = headers, params = query).get(timeout = timeout)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("JX3API 返回的数据格式异常。")

    if "status" in payload and "detail" in payload:
        status = payload["status"]
        return {
            **payload,
            "code": status,
            "data": payload["detail"] if status == 200 else None,
            "msg": "" if status == 200 else str(payload["detail"] or "查询失败，请稍后重试！"),
        }
    if "code" in payload:
        return {"msg": "", "data": None, **payload}
    raise ValueError("JX3API 返回的数据格式异常。")
