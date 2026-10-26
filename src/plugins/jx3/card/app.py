"""Command parsing, material discovery, role lookup and off-thread rendering."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
import math
import shlex

from .catalog import BODY_ALIASES, CATEGORIES, LABELS, PAGE_SIZE, get_catalog
from .renderer import Renderer, Role


_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix='social-card')
_PENDING = 0
MAX_PENDING = 24


@dataclass(frozen=True)
class CardRequest:
    server: str
    identifier: str
    signature: str
    background: str
    avatar: str
    frame: str


@dataclass(frozen=True)
class BrowseRequest:
    category: str
    page: int = 1
    keyword: str = ''
    body: str | None = None


@dataclass(frozen=True)
class PreviewRequest:
    category: str
    value: str


@dataclass(frozen=True)
class Result:
    text: str = ''
    image: bytes | None = None


def help_text() -> str:
    catalog = get_catalog()
    return (
        '社交名片 服务器 ID 签名 背景 头像 头像框\n'
        'ID 为游戏角色名；签名含空格可加双引号。后三项可填编号或名称。\n\n'
        f'背景 {len(catalog.entries("backgrounds"))} 款 / '
        f'头像 {len(catalog.entries("avatars"))} 款 / '
        f'头像框 {len(catalog.entries("frames"))} 款\n'
        '看图挑选：社交名片 背景 / 社交名片 头像 / 社交名片 头像框\n'
        '翻页：社交名片 头像 2\n'
        '搜索：社交名片 头像 心上砂\n'
        '单项大图：社交名片 预览 头像 314\n'
        '阵营、门派、体型取自角色详情；头像体型自动匹配，无需填写。'
    )


def parse_arguments(text: str) -> CardRequest | BrowseRequest | PreviewRequest | None:
    if len(text) > 1024:
        raise ValueError('参数过长，请缩短签名或搜索关键词。')
    try:
        args = shlex.split(text)
    except ValueError as error:
        raise ValueError('引号未闭合，请在签名两侧使用成对的英文双引号。') from error
    if not args or args[0] in {'帮助', 'help', '?', '？'}:
        return None
    if args[0] in {'素材', '图鉴', '列表'}:
        args.pop(0)
        if not args:
            return None
    if args[0] == '预览':
        if len(args) != 3 or args[1] not in CATEGORIES:
            raise ValueError('格式：社交名片 预览 背景/头像/头像框 编号或名称\n例：社交名片 预览 头像 314')
        return PreviewRequest(CATEGORIES[args[1]], args[2])
    if args[0] in CATEGORIES:
        category, page, body, words = CATEGORIES[args[0]], None, None, []
        for arg in args[1:]:
            if arg.isascii() and arg.isdecimal():
                if page is not None:
                    raise ValueError('只需填写一个页码；按编号搜索时请使用“搜索=314”。')
                page = int(arg)
                if page < 1:
                    raise ValueError('页码从 1 开始。')
            elif arg.lower() in BODY_ALIASES and category == 'avatars':
                if body is not None:
                    raise ValueError('每次只能筛选一种体型。不填写体型可查看四种版本。')
                body = BODY_ALIASES[arg.lower()]
            else:
                words.append(arg.removeprefix('搜索='))
        return BrowseRequest(category, page or 1, ' '.join(words), body)
    if len(args) < 6:
        raise ValueError(help_text())
    # The last three arguments are unambiguous; allow an unquoted multiword
    # signature as well as the documented quoted form.
    server, identifier = args[:2]
    signature = ' '.join(args[2:-3])
    if any(len(value) > 80 for value in [server, identifier, *args[-3:]]) or len(signature) > 120:
        raise ValueError('服务器、ID、素材名称最多 80 字，签名最多 120 字；过长的显示文字会自动省略。')
    if not server or not identifier or any(not value for value in args[-3:]):
        raise ValueError('服务器、角色名和三项素材不能为空。')
    return CardRequest(server, identifier, signature, *args[-3:])


async def lookup_role(server_name: str, identifier: str) -> Role:
    # Keep offline help, catalogues and tests independent of bot configuration.
    from src.const.jx3.server import Server
    from src.const.jx3.school import School
    from .api import fetch_role

    server = Server(server_name).server
    if not server:
        raise ValueError('未识别该服务器，请检查服务器名称或别名。')
    role = await fetch_role(server, identifier)
    return replace(role, school=School(role.school).name or role.school)


async def render_async(function, *args):
    return await asyncio.get_running_loop().run_in_executor(_EXECUTOR, function, *args)


def personal_ui_color(user_id: str | None) -> str:
    if user_id is None:
        return '默认'
    from src.utils.database import db
    from src.utils.database.classes import PersonalSettings
    settings = db.where_one(PersonalSettings(), 'user_id = ?', str(user_id), default=None)
    return settings.setting.ui_color if settings is not None else '默认'


async def execute(text: str, user_id: str | None = None) -> Result:
    request = parse_arguments(text)
    if request is None:
        return Result(help_text())
    catalog = get_catalog()
    ui_color = personal_ui_color(user_id) if isinstance(request, (BrowseRequest, PreviewRequest)) else '默认'
    renderer = Renderer(catalog, ui_color=ui_color)
    if isinstance(request, BrowseRequest):
        entries = catalog.search(request.category, request.keyword, request.body)
        label = LABELS[request.category]
        if not entries:
            return Result(f'没有找到匹配的{label}。发送“社交名片 {label}”查看全部可选项。')
        pages = math.ceil(len(entries) / PAGE_SIZE)
        if request.page > pages:
            raise ValueError(f'当前结果共有 {pages} 页，请输入 1～{pages}。')
        content = await render_async(renderer.gallery, request.category, entries, request.page, request.keyword, request.body)
        suffix = f' {shlex.quote("搜索=" + request.keyword)}' if request.keyword else ''
        suffix += f' {request.body}' if request.body else ''
        more = f'\n下一页：社交名片 {label} {request.page + 1}{suffix}' if request.page < pages else ''
        return Result(f'{label}图鉴 {request.page}/{pages} 页（共 {len(entries)} 项）。'
                      f'{more}\n单项预览：社交名片 预览 {label} 编号\n生成时可填写图中的编号或名称。', content)
    if isinstance(request, PreviewRequest):
        selection = catalog.resolve(request.category, request.value)
        content = await render_async(renderer.preview, request.category, selection)
        item = selection.entry
        return Result(f'{LABELS[request.category]}：{item["name"]}\n可填：{item["id"]} 或 {item["name"]}', content)
    # Validate all material choices before spending a role lookup request.
    background = catalog.resolve('backgrounds', request.background)
    avatar = catalog.resolve('avatars', request.avatar)
    frame = catalog.resolve('frames', request.frame)
    try:
        role = await asyncio.wait_for(lookup_role(request.server, request.identifier), timeout=30)
    except asyncio.TimeoutError as error:
        raise ValueError('角色查询超时，请稍后重试。素材图鉴仍可正常查看。') from error
    content = await render_async(renderer.card, role, request.signature, background, avatar, frame)
    return Result(image=content)


async def execute_async(text: str, user_id: str | None = None) -> Result:
    global _PENDING
    # Bound concurrent API queries and the single rendering worker's backlog.
    # Track the task through cancellation until it really exits the executor.
    if _PENDING >= MAX_PENDING:
        raise ValueError('社交名片任务较多，请稍后再试。')
    _PENDING += 1

    async def work():
        global _PENDING
        try:
            return await execute(text, user_id)
        finally:
            _PENDING -= 1

    task = asyncio.create_task(work())
    task.add_done_callback(lambda done: None if done.cancelled() else done.exception())
    return await asyncio.shield(task)


async def shutdown_renderer():
    await asyncio.to_thread(_EXECUTOR.shutdown, wait=True)
