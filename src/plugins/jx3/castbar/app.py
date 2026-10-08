"""Robot command parsing and in-memory castbar generation."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import lru_cache
import io
import math
import re
import shlex
import threading

from . import renderer
from .cache import ByteCache
from .fonts import enumerate_fonts

HELP = """读条 职业 [名称] [时长] [正/倒] [小节] [尺寸]
例：读条 长歌 徵 2.12 正
例：读条 七秀 回雪飘摇 3 倒 6 640x158
例：读条 长歌 徵 2 正 格式=png 时间=0.71 宽=640
可省略可识别的参数；用 - 跳过一个位置。含空格的名称加双引号。
也可全部使用 参数=值，或与简写混用；参数=值优先。
默认：职业原技能名、2.12 秒、正读条、4 小节、2 倍尺寸、完整 GIF、游戏字体及粒子。
参数：职业、名称、时长、方向、时间（当前帧）、格式=png/gif/apng、范围=完整/当前、宽、高、尺寸、倍率=1/2/3、小节=数量/关、粒子=开/关、强度=0~2、字体、字号=8~36、计时=开/关、背景=透明/深色/浅色、帧率=10/20/30。
只填宽或高自动保持比例；同时填宽高可拉伸。
读条 职业：列出职业；读条 字体 [关键词]：查询机器人主机字体。
APNG 以文件发送，GIF/PNG 以图片发送。
生成任务按顺序排队，同时只生成一张；排队结束后自动发送。"""

SCHOOL_ALIASES = {style['id']: style['id'] for style in renderer.STYLES}
SCHOOL_ALIASES.update({style['name']: style['id'] for style in renderer.STYLES})
SCHOOL_ALIASES.update({
    '万花': 'wanhua', '凌雪': 'lingxue', '衍天': 'yantian', '万灵山庄': 'wanling',
    '无相': 'wuxiang', '药王谷': 'yaozong', '剑纯': 'chunyang', '气纯': 'chunyang',
    '相知': 'changge', '莫问': 'changge', '冰心': 'qixiu', '云裳': 'qixiu',
    '花间': 'wanhua', '离经': 'wanhua', '毒经': 'wudu', '补天': 'wudu',
})
DIRECTIONS = {'正': 'forward', '正读条': 'forward', '正读': 'forward', 'forward': 'forward',
              '倒': 'reverse', '倒读条': 'reverse', '倒读': 'reverse', 'reverse': 'reverse'}
OPTIONS = {'职业', '方向', '时长', '名称', '时间', '格式', '范围', '宽', '高', '尺寸', '倍率', '小节',
           '粒子', '强度', '字体', '字号', '计时', '背景', '帧率'}
OPTION_ALIASES = {key: key for key in OPTIONS}
OPTION_ALIASES.update({
    '门派': '职业', 'school': '职业', 'job': '职业',
    '技能': '名称', '技能名': '名称', 'name': '名称', 'skill': '名称',
    '总时长': '时长', 'duration': '时长', 'direction': '方向',
    'time': '时间', 'elapsed': '时间', 'format': '格式', 'range': '范围',
    'width': '宽', 'height': '高', 'size': '尺寸', 'scale': '倍率',
    'segments': '小节', '小节数': '小节', 'particles': '粒子', 'strength': '强度',
    'font': '字体', 'fontsize': '字号', 'showtime': '计时', 'background': '背景', 'fps': '帧率',
})
POSITIONAL_FIELDS = ('名称', '时长', '方向', '小节', '尺寸')
SIZE_PATTERN = re.compile(r'(\d+)\s*[xX×]\s*(\d+)')
IMAGE_CACHE = ByteCache(max_bytes=32 * 1024 * 1024, max_entries=64)
_RENDER_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix='castbar')
_QUEUE_LOCK = threading.Lock()
_QUEUED_JOBS = []


@dataclass(frozen=True)
class GeneratedImage:
    content: bytes
    filename: str
    format: str


def split_command(text: str) -> list[str]:
    if len(text) > 2048:
        raise ValueError('参数过长，请缩短名称或字体名称。')
    try:
        return shlex.split(text.replace('＝', '='))
    except ValueError as error:
        raise ValueError('引号未闭合，含空格的名称请用双引号括起来。') from error


def _toggle(value: str) -> bool:
    if value in {'开', '开启', '是', 'on', 'true', '1'}:
        return True
    if value in {'关', '关闭', '否', 'off', 'false', '0'}:
        return False
    raise ValueError('开关参数请填写“开”或“关”。')


def _number(value: str, label: str, integer: bool = False):
    try:
        number = float(value.removesuffix('秒').removesuffix('px'))
    except ValueError as error:
        raise ValueError(f'{label}须为数字。') from error
    if not math.isfinite(number) or (integer and not number.is_integer()):
        raise ValueError(f'{label}须为有限的' + ('整数。' if integer else '数字。'))
    return int(number) if integer else number


@lru_cache(maxsize=1)
def font_catalog():
    fonts = enumerate_fonts([renderer.GAME_FONT_PATH])
    renderer.FONTS_BY_ID.update({font['id']: font for font in fonts})
    return fonts


def _font_id(query: str) -> str:
    if query in {'默认', '游戏', '游戏默认'}:
        return renderer.DEFAULT_FONT['id']
    query = query.casefold()
    fonts = font_catalog()
    fields = ('id', 'label', 'family', 'fullName', 'postscriptName')
    exact = [font for font in fonts if any(str(font.get(key, '')).casefold() == query for key in fields)]
    matches = exact or [font for font in fonts if query in str(font['label']).casefold()]
    if len(matches) == 1:
        return matches[0]['id']
    if not matches:
        raise ValueError('未找到字体，请用“读条 字体 关键词”查询机器人主机已安装字体。')
    labels = '、'.join(font['label'] for font in matches[:6])
    raise ValueError(f'匹配到多个字体，请使用完整字体名称：{labels}')


def information(text: str) -> str | None:
    tokens = split_command(text)
    if not tokens or tokens[0] in {'帮助', 'help', '-h', '--help'}:
        return HELP
    if tokens[0] in {'职业', '列表'}:
        return '可选职业：' + '、'.join('万花' if style['id'] == 'wanhua' else style['name'] for style in renderer.STYLES)
    if tokens[0] != '字体':
        return None
    query = ' '.join(tokens[1:]).casefold()
    matches = [font for font in font_catalog() if query in str(font['label']).casefold()]
    if not matches:
        return '未找到匹配字体。默认可用“方正黑体_GBK”。'
    labels = '\n'.join(font['label'] for font in matches[:30])
    return f'机器人主机字体（匹配 {len(matches)} 项）：\n{labels}' + ('\n请加关键词缩小范围。' if len(matches)>30 else '')


async def information_async(text: str) -> str | None:
    tokens = split_command(text)
    if tokens and tokens[0] == '字体':
        return await asyncio.to_thread(information, text)
    # Ordinary commands must reach the queue before yielding, preserving order.
    return information(text)


def _numeric_token(token: str) -> bool:
    try:
        float(token.removesuffix('秒').removesuffix('px'))
        return True
    except ValueError:
        return False


def _positional_match(field: str, token: str) -> bool:
    if field == '名称':
        return not (_numeric_token(token) or token.casefold() in DIRECTIONS or SIZE_PATTERN.fullmatch(token))
    if field in {'时长', '小节'}:
        return _numeric_token(token) or (field == '小节' and token in {'关', '关闭', 'off'})
    if field == '方向':
        return token.casefold() in DIRECTIONS
    return SIZE_PATTERN.fullmatch(token) is not None


def _command_options(text: str) -> dict[str, str]:
    tokens = split_command(text)
    if not tokens:
        raise ValueError(HELP)
    named = {}
    positional = []
    for token in tokens:
        if '=' in token:
            key, value = token.split('=', 1)
            canonical = OPTION_ALIASES.get(key.casefold())
            if canonical is None:
                raise ValueError(f'未知参数“{key}”，请用“读条 帮助”查看支持的参数。')
            if canonical in named:
                raise ValueError(f'参数“{canonical}”重复。')
            named[canonical] = value
        else:
            positional.append(token)
    options = {}
    if positional and positional[0].casefold() in SCHOOL_ALIASES:
        options['职业'] = positional.pop(0)
    elif '职业' not in named:
        raise ValueError('未找到职业，请用“读条 职业”查看列表。')
    fields = POSITIONAL_FIELDS
    # Keep the previous direction-first shorthand working during migration.
    if positional and positional[0].casefold() in DIRECTIONS:
        fields = ('方向', '时长', '名称', '小节', '尺寸')
    cursor = 0
    for token in positional:
        if token in {'-', '_'}:
            if cursor >= len(fields):
                raise ValueError('简写参数过多。')
            cursor += 1
            continue
        while cursor < len(fields) and not _positional_match(fields[cursor], token):
            cursor += 1
        if cursor >= len(fields):
            raise ValueError('简写顺序：职业 名称 时长 正/倒 小节 尺寸；其他参数请用“参数=值”。')
        options[fields[cursor]] = token
        cursor += 1
    options.update(named)
    return options


def parse_request(text: str) -> tuple[dict, str]:
    options = _command_options(text)
    school = SCHOOL_ALIASES.get(options['职业'].casefold())
    if school is None:
        raise ValueError('未找到职业，请用“读条 职业”查看列表。')
    request = {'school': school}
    if '方向' in options:
        direction = DIRECTIONS.get(options['方向'].casefold())
        if direction is None:
            raise ValueError('方向须为正或倒。')
        request['direction'] = direction
    if '名称' in options:
        if len(options['名称']) > 40:
            raise ValueError('技能名称最多 40 个字符。')
        request['skill'] = options['名称']
    for key, field, integer in [('时长', 'duration', False), ('时间', 'elapsed', False), ('强度', 'strength', False),
                                ('字号', 'fontSize', True), ('帧率', 'fps', True), ('倍率', 'scale', True)]:
        if key in options:
            request[field] = _number(options[key], key, integer)
    if request.get('scale', 2) not in [1, 2, 3]:
        raise ValueError('倍率须为 1、2 或 3。')
    if '尺寸' in options:
        if '宽' in options or '高' in options:
            raise ValueError('“尺寸”与“宽/高”请选一种写法。')
        match = SIZE_PATTERN.fullmatch(options['尺寸'])
        if not match:
            raise ValueError('尺寸请填写宽x高，例如“尺寸=640x158”。')
        request['width'], request['height'] = map(int, match.groups())
    elif '宽' in options or '高' in options:
        scene = renderer.BY_ID[school]
        width = _number(options['宽'], '宽度', True) if '宽' in options else None
        height = _number(options['高'], '高度', True) if '高' in options else None
        request['width'] = width if width is not None else round(height*scene['width']/scene['height'])
        request['height'] = height if height is not None else round(width*scene['height']/scene['width'])
    for key, field in [('粒子', 'particles'), ('计时', 'showTime')]:
        if key in options:
            request[field] = _toggle(options[key].casefold())
    if '小节' in options:
        value = options['小节']
        if value in {'关', '关闭', 'off', '0'}:
            request['showSegments'] = False
        else:
            request['segments'] = _number(value, '小节数量', True)
    if '背景' in options:
        backgrounds = {'透明': 'transparent', '深色': 'dark', '浅色': 'light',
                       'transparent': 'transparent', 'dark': 'dark', 'light': 'light'}
        if options['背景'] not in backgrounds:
            raise ValueError('背景须为透明、深色或浅色。')
        request['background'] = backgrounds[options['背景']]
    if '范围' in options:
        ranges = {'完整': 'full', '当前': 'current', 'full': 'full', 'current': 'current'}
        if options['范围'] not in ranges:
            raise ValueError('范围须为完整或当前。')
        request['exportEnd'] = ranges[options['范围']]
    if '字体' in options:
        if not options['字体'].strip():
            raise ValueError('字体名称不能为空。')
        request['fontId'] = _font_id(options['字体'])
    format_ = options.get('格式', 'gif').lower()
    if format_ not in {'png', 'gif', 'apng'}:
        raise ValueError('格式须为 png、gif 或 apng。')
    return renderer.settings(request), format_


def generate_image(text: str) -> GeneratedImage:
    # The worker retains the lock even if its awaiting coroutine is cancelled.
    with renderer.EXPORT_LOCK:
        data, format_ = parse_request(text)
        key = (format_, tuple(sorted(data.items())))
        cached = IMAGE_CACHE.get(key)
        if cached is not None:
            return cached
        if format_ == 'gif':
            content = renderer.gif_bytes(data)
        elif format_ == 'apng':
            content = renderer.apng_bytes(data)
        else:
            output = io.BytesIO()
            renderer.render(data, data['elapsed']).save(output, format='PNG')
            content = output.getvalue()
        suffix = 'apng.png' if format_ == 'apng' else format_
        filename = f"castbar_{data['school']}_{data['direction']}_{data['width']}x{data['height']}.{suffix}"
        image = GeneratedImage(content, filename, format_)
        IMAGE_CACHE.put(key, image, len(content))
        return image


def _remove_finished_job(future):
    with _QUEUE_LOCK:
        _QUEUED_JOBS.remove(future)


async def generate_image_async(text: str, on_queued=None) -> GeneratedImage:
    """Submit in arrival order without occupying the bot's default thread pool."""
    with _QUEUE_LOCK:
        ahead = sum(not job.done() for job in _QUEUED_JOBS)
        future = _RENDER_EXECUTOR.submit(generate_image, text)
        _QUEUED_JOBS.append(future)
    future.add_done_callback(_remove_finished_job)
    pending = asyncio.wrap_future(future)
    try:
        if ahead and on_queued is not None:
            await on_queued(ahead)
        return await pending
    except BaseException:
        # Pending jobs can be skipped; running threads finish before the next job.
        future.cancel()
        pending.cancel()
        raise
