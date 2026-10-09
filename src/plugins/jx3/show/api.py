from typing import Literal
from urllib.parse import urlparse

import httpx

from src.config import Config
from src.const.jx3.server import Server
from src.utils.network import Request
from src.utils.database.classes import RoleData


class RoleCardServiceError(ValueError):
    """An upstream service failure, rather than invalid command arguments."""


def _json_object(response: httpx.Response, stage: str) -> dict:
    if not 200 <= response.status_code < 300:
        raise RoleCardServiceError(f'{stage}失败（HTTP {response.status_code}），请检查服务状态。')
    if not response.content.strip():
        raise RoleCardServiceError(f'{stage}返回空响应，请检查服务状态。')
    try:
        payload = response.json()
    except ValueError:
        raise RoleCardServiceError(f'{stage}返回非 JSON 响应，请检查服务地址和状态。') from None
    if not isinstance(payload, dict):
        raise RoleCardServiceError(f'{stage}返回的数据格式不正确。')
    return payload


async def get_role_card_url(role_data: RoleData) -> tuple[str, int] | Literal[False]:
    server = Server(role_data.serverName)
    params = {
        'game_global_role_id': role_data.globalRoleId,
        'game_role_id': role_data.roleId,
        'zone': server.zone,
        'server': server.server,
    }
    try:
        response = await Request('https://m.pvp.xoyo.com/badge/get-role-card-preset', params=params).post(tuilan=True)
    except httpx.HTTPError:
        raise RoleCardServiceError('推栏名片查询连接失败，请稍后重试。') from None
    payload = _json_object(response, '推栏名片查询')
    if payload.get('code') != 0:
        return False
    data = payload.get('data')
    if not isinstance(data, dict) or not isinstance(data.get('showCardPresetUrl'), str) or not data['showCardPresetUrl']:
        raise RoleCardServiceError('推栏名片查询没有返回有效的名片数据。')
    decoder = Config.jx3.api.cqc_url.rstrip('/')
    if not decoder:
        raise RoleCardServiceError('名片解析服务地址未配置，请设置 jx3.api.cqc_url。')
    try:
        response = await Request(decoder + '/role_card', params={'showCardPresetUrl': data['showCardPresetUrl']}).get()
    except httpx.HTTPError:
        raise RoleCardServiceError('名片解析服务连接失败，请检查 jx3.api.cqc_url 对应的服务。') from None
    result = _json_object(response, '名片解析服务')
    url = result.get('url')
    if not isinstance(url, str) or urlparse(url).scheme not in {'http', 'https'} or not urlparse(url).netloc:
        raise RoleCardServiceError('名片解析服务没有返回有效的图片地址。')
    return url, data.get('praiseTotalCount', 0)
