"""Resolve image sources using the bot's existing role-card lookup."""
from urllib.parse import urlparse

from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.database.player import search_player
from src.plugins.jx3.show.api import get_role_card_url

from .client import PindouServiceError


def resolve_card_server(server_name: str) -> str:
    try:
        # The command requires an explicit server. Never fall back to a group's
        # server if the supplied name is invalid and query the wrong character.
        server = Server(server_name).server
    except Exception as exc:
        raise PindouServiceError(PROMPT.ServerInvalid) from exc
    if not server:
        raise PindouServiceError(PROMPT.ServerInvalid)
    return server


async def get_card_image_url(server_name: str, role_name: str) -> str:
    server = resolve_card_server(server_name)

    try:
        role = await search_player(role_name=role_name, server_name=server)
        found = bool(role and role.roleId)
    except Exception as exc:
        raise PindouServiceError("角色查询失败，请稍后重试。") from exc
    if not found:
        raise PindouServiceError(PROMPT.PlayerNotExist)

    try:
        card = await get_role_card_url(role)
    except Exception as exc:
        raise PindouServiceError("名片查询失败，请稍后重试。") from exc
    if not card:
        raise PindouServiceError(PROMPT.PlayerNotExist)
    try:
        if not isinstance(card, (tuple, list)) or len(card) != 2:
            raise ValueError("card response")
        url = card[0]
        if not isinstance(url, str):
            raise ValueError("card url")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("card url")
    except (TypeError, ValueError) as exc:
        raise PindouServiceError("名片服务未返回有效的图片地址，请稍后重试。") from exc
    return url
