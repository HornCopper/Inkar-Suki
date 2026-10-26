"""Use the same JX3API /role/detail source as the existing 玩家 command."""
import httpx

from .catalog import BODY_ALIASES
from .renderer import Role


def parse_role_response(payload: dict, server: str, identifier: str) -> Role:
    if not isinstance(payload, dict):
        raise ValueError('角色详情返回的数据格式异常，请稍后重试。')
    if payload.get('code') == 404:
        raise ValueError('未找到该角色，请检查服务器和 ID；角色在世界频道发言后可能才可查询。')
    if payload.get('code') != 200:
        raise ValueError('角色详情查询未成功，请稍后重试。')
    data = payload.get('data')
    if not isinstance(data, dict):
        raise ValueError('角色详情没有返回有效的角色数据。')
    body = data.get('bodyName')
    if not isinstance(body, str) or body.casefold() not in BODY_ALIASES:
        raise ValueError('角色详情未提供可识别的体型，暂时无法生成名片，请稍后重试。')
    camp = data.get('campName')
    school = data.get('forceName')
    if not isinstance(camp, str) or not camp or not isinstance(school, str) or not school:
        raise ValueError('角色详情缺少阵营或门派，请稍后重试。')
    # The renderer configures display level separately from these API fields.
    return Role(name=data.get('roleName') or identifier, server=data.get('serverName') or server,
                school=school, camp=camp, body=body)


async def fetch_role(server: str, identifier: str) -> Role:
    from src.config import Config
    from src.utils.network import Request

    if not Config.jx3.api.enable or not Config.jx3.api.token:
        raise ValueError('机器人尚未配置可用的 JX3API 角色查询服务，请联系管理员。')
    params = {'token': Config.jx3.api.token, 'server': server, 'name': identifier}
    try:
        response = await Request(f'{Config.jx3.api.url}/role/detail', params=params).get(timeout=20)
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError):
        # Keep token-bearing request URLs out of error messages and tracebacks.
        raise ValueError('角色详情接口暂时不可用，请稍后重试。') from None
    return parse_role_response(payload, server, identifier)
