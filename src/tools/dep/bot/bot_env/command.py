
import nonebot
from nonebot import on_command
from sgtpyutils.logger import logger


def __start_hook_on_command():
    logger.debug('hooked func on_command')
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
