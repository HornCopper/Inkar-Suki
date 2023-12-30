
import nonebot
from nonebot import on_command
from sgtpyutils.logger import logger
from .document import DocumentGenerator

import nonebot.matcher


def __start_hook_command_handler():
    logger.debug('hooked func on_command.handle')
    @DocumentGenerator.counter
    def __hook_on_command_handle(cls, parameterless):
        return nonebot.matcher.Matcher._handle(cls, parameterless)
    nonebot.matcher.Matcher._handle = nonebot.matcher.Matcher.handle  # 初始化
    nonebot.matcher.Matcher.handle = __hook_on_command_handle


def __start_hook_on_command():
    logger.debug('hooked func on_command')

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
        return nonebot._on_command(cmd, rule, aliases, force_whitespace,  _depth, **kwargs)
    nonebot._on_command = nonebot.on_command  # 初始化
    nonebot.on_command = __hook_on_command


__start_hook_on_command()
__start_hook_command_handler()