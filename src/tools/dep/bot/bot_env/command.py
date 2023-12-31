
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
    description: str = None,
    **kwargs,
):
    force_whitespace = ' '
    command_item = nonebot._on_command(cmd, rule, aliases, force_whitespace,  _depth)

    # def on_call_self(*args, **kwargs):
    #     return __hook_on_command_handle(command_item, *args, **kwargs)
    # command_item.handle = on_call_self
    return command_item
nonebot._on_command = nonebot.on_command  # 初始化
nonebot.on_command = __hook_on_command


