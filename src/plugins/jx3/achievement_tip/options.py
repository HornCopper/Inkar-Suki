"""Quote-free arguments for custom achievement notifications."""
from dataclasses import dataclass
import re


HELP = """成就提示 标题 [描述] [资历] [png/gif]
例：成就提示 成功下班 今天没有加班 100
例：成就提示 今日不鸽 准时参加团本 25 png
也可用：成就提示 标题=Happy Weekend 描述=今天没有加班 资历=100
无需引号：第一个词是标题，末尾独立整数是资历，中间文字是描述。
也可明确使用“资历=100”；显式资历参数优先，此时描述中的数字保留。
同一条消息可附一张图片作为图标，自动居中裁成正方形。
未附图时提示补发图片；回复“头像”使用你的 QQ 头像，回复“五甲”或“无伤”使用对应预设图标。
回复其他内容则取消本次生成。
固定尺寸 806×276，默认资历 0、GIF，动画总时长固定 3 秒。
字号固定，文字过长截断并加上三个点“...”。
末尾可写 png 或 gif，也可使用“格式=png/gif/apng”。
GIF 无限循环，每轮 3 秒；PNG 为外围透明的静态图，只保留盖章完成的提示条；APNG 作为文件发送。
全部内容自定义，不查询游戏成就。"""

ALIASES = {
    '标题': 'title', 'title': 'title',
    '描述': 'description', 'description': 'description', 'desc': 'description',
    '资历': 'points', 'points': 'points',
    '格式': 'format', 'format': 'format',
}
TEXT_FIELDS = {'title', 'description'}
OPTION_KEY = re.compile(r'^[A-Za-z_\u4e00-\u9fff]+$')


@dataclass(frozen=True)
class TipRequest:
    title: str
    description: str = ''
    points: int = 0
    format: str = 'gif'

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError('请填写标题。\n例：成就提示 成功下班 今天没有加班 资历=100')
        if len(self.title) > 60 or len(self.description) > 300:
            raise ValueError('标题最多 60 个字符，描述最多 300 个字符。')
        if not isinstance(self.points, int) or not 0 <= self.points <= 999999:
            raise ValueError('资历须为 0～999999 的整数。')
        if self.format not in {'png', 'gif', 'apng'}:
            raise ValueError('格式须为 png、gif 或 apng。')


def information(text: str) -> str | None:
    if text.strip().lower() in {'', '帮助', 'help', '-h', '--help'}:
        return HELP
    return None


def parse_request(text: str) -> TipRequest:
    if len(text) > 2048:
        raise ValueError('命令过长，请缩短标题和描述。')
    named: dict[str, str] = {}
    positional: list[str] = []
    current_field = None
    for token in text.split():
        key, separator, value = token.replace('＝', '=').partition('=')
        if separator and OPTION_KEY.fullmatch(key):
            field = ALIASES.get(key.lower())
            if field is None:
                raise ValueError(f'不支持参数“{key}”。尺寸固定；请用“成就提示 帮助”查看参数。')
            if field in named:
                raise ValueError(f'参数“{key}”重复。')
            named[field] = value
            current_field = field if field in TEXT_FIELDS else None
        elif current_field is not None:
            named[current_field] += ' ' + token
        else:
            positional.append(token)

    # Read the optional output format before the trailing points shorthand.
    if len(positional) > 1 and positional[-1].lower() in {'png', 'gif'}:
        if 'format' in named:
            raise ValueError('格式重复，请使用末尾 png/gif 或“格式=”其中一种写法。')
        named['format'] = positional.pop().lower()

    points_text = named.get('points')
    # Reserve the first word for the title, even when it is numeric. An
    # explicit points option keeps a numeric description suffix literal.
    if points_text is None and len(positional) > 1 and re.fullmatch(r'[0-9]+', positional[-1]):
        points_text = positional.pop()

    title = positional[0] if positional else ''
    description = ' '.join(positional[1:])
    if 'title' in named:
        if title:
            raise ValueError('标题重复，请使用简写或“标题=”其中一种写法。')
        title = named['title'].strip()
    if 'description' in named:
        if description:
            raise ValueError('描述重复，请使用简写或“描述=”其中一种写法。')
        description = named['description'].strip()

    if points_text is None:
        points_text = '0'
    if not re.fullmatch(r'[0-9]{1,6}', points_text):
        raise ValueError('资历须为 0～999999 的整数，请使用“资历=100”这样的写法。')
    return TipRequest(title, description, int(points_text),
                      named.get('format', 'gif').lower())
