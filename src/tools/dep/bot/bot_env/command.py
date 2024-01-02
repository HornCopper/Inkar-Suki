
import nonebot
from sgtpyutils.logger import logger
from .document import DocumentGenerator

import nonebot.matcher


logger.debug('hooked func on_command')


@DocumentGenerator.counter
def __hook_on_command_handle(cls, parameterless=None):
    return nonebot.matcher.Matcher.handle(parameterless)


@DocumentGenerator.register
def __hook_on_command(
    cmd,
    rule=None,
    aliases=None,
    force_whitespace=None,
    _depth: int = 0,
    **kwargs,
):
    force_whitespace = ' '
    command_item = nonebot._on_command(cmd, rule, aliases, force_whitespace,  _depth)
    return command_item


nonebot._on_command = nonebot.on_command  # 初始化
nonebot.on_command = __hook_on_command


@DocumentGenerator.register
def __hook_on_regex(
    pattern: str,
    flags=0,
    rule=None,
    _depth: int = 0,
    **kwargs,
):
    # 添加一个精确匹配
    command_item = nonebot._on_regex(f'{pattern}$', flags, rule, _depth)
    # 和常规匹配
    command_item = nonebot._on_regex(pattern, flags, rule, _depth)
    return command_item


nonebot._on_regex = nonebot.on_regex  # 初始化
nonebot.on_regex = __hook_on_regex
