"""Resolve existing role-card sources and render on a dedicated single thread."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import lru_cache
import shlex
from pathlib import Path
from urllib.parse import urlparse

import httpx

from src.utils.serendipity_image import compose_serendipity_image
from .card_layout import Placement, composite_card, SIZE_RATIOS


ASSETS = Path(__file__).resolve().parents[3] / 'assets'
_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix='qiyu-card')
MAX_DOWNLOAD_BYTES = 15 * 1024 * 1024
HELP = '格式：奇遇名片 服务器 ID 奇遇 [特大/大/中/小]\n例：奇遇名片 梦江南 取净湖 三山四海 大\nID 指游戏角色名；尺寸默认中，按名片尺寸计算。多个请求会依次排队并自动发送。'


@dataclass(frozen=True)
class CardRequest:
    server: str
    identifier: str
    serendipity: str
    size: str = '中'


def parse_arguments(text: str) -> CardRequest:
    try:
        args = shlex.split(text)
    except ValueError as error:
        raise ValueError('引号未闭合。\n' + HELP) from error
    if len(args) not in (3, 4):
        raise ValueError(HELP)
    if any(len(value) > 80 for value in args):
        raise ValueError('参数过长，请检查服务器、ID 和奇遇名称。')
    if len(args) == 4 and args[3] not in SIZE_RATIOS:
        raise ValueError('尺寸只能选择特大、大、中、小。\n' + HELP)
    return CardRequest(*args)


@lru_cache(maxsize=2)
def illustration_catalogue(assets: Path) -> dict[str, tuple[Path, ...]]:
    root = assets / 'image/jx3/serendipity/show'
    result = {}
    for category in ('common', 'peerless', 'pet'):
        for path in (root / category).glob('*.png'):
            result.setdefault(path.stem.split('-', 1)[0], []).append(path)
    return {name: tuple(paths) for name, paths in result.items()}


def validate_serendipity(name: str):
    if name not in illustration_catalogue(ASSETS):
        raise ValueError(f'未找到奇遇「{name}」的插图，请检查奇遇名称。')


def resolve_illustration(name: str, school: str = '') -> Path:
    # Compare known stems, never interpret user input as a file path.
    validate_serendipity(name)
    matches = illustration_catalogue(ASSETS)[name]
    for path in matches:
        if path.stem == name:
            return path
    for path in matches:
        if path.stem == f'{name}-{school}':
            return path
    raise ValueError('该奇遇需要门派对应的插图，但角色门派信息没有匹配资源。')


def render_card(card_bytes: bytes, name: str, school: str = '', size: str = '中') -> tuple[bytes, Placement]:
    path = resolve_illustration(name, school)
    popup = compose_serendipity_image(path, ASSETS)
    return composite_card(card_bytes, popup, size=size)


async def render_card_async(card_bytes: bytes, name: str, school: str = '', size: str = '中') -> tuple[bytes, Placement]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_EXECUTOR, render_card, card_bytes, name, school, size)


async def download_card(url: str) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
        raise ValueError('名片服务没有返回有效的图片地址。')
    chunks, total = [], 0
    async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
        async with client.stream('GET', url) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes():
                total += len(chunk)
                if total > MAX_DOWNLOAD_BYTES:
                    raise ValueError('名片图片超过 15 MB，暂时无法生成。')
                chunks.append(chunk)
    return b''.join(chunks)


async def generate_card(request: CardRequest) -> tuple[bytes, Placement]:
    await asyncio.get_running_loop().run_in_executor(_EXECUTOR, validate_serendipity, request.serendipity)
    # Imported here to keep the algorithm and queue independently testable,
    # without starting the bot or opening its databases.
    from src.utils.database.player import search_player
    from src.const.jx3.school import School
    from .api import get_role_card_url

    try:
        role = await search_player(role_name=request.identifier, server_name=request.server)
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as error:
        raise ValueError('角色查询接口返回异常，请检查角色查询服务状态。') from error
    if not role or not role.roleId:
        raise ValueError('未找到该角色，请检查服务器和 ID。')
    card = await get_role_card_url(role)
    if not card:
        raise ValueError('未找到该角色的名片，请稍后重试。')
    card_bytes = await download_card(card[0])
    school = School(role.forceName).name or role.forceName
    return await render_card_async(card_bytes, request.serendipity, school, request.size)


async def shutdown_renderer():
    await asyncio.to_thread(_EXECUTOR.shutdown, wait=True)
