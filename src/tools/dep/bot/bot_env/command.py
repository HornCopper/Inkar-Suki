
from typing import overload
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from sgtpyutils.functools import AssignableArg
import functools
import nonebot
from sgtpyutils.logger import logger
from .document import DocumentGenerator, DocumentItem

import nonebot.matcher
from nonebot.matcher import Matcher

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
    if not pattern[-1] == '$':
        command_item = nonebot._on_regex(f'{pattern}$', flags, rule, _depth)
    # 和常规匹配
    command_item = nonebot._on_regex(f'{pattern}', flags, rule, _depth)
    return command_item


nonebot._on_regex = nonebot.on_regex  # 初始化
nonebot.on_regex = __hook_on_regex


@overload
def get_cmd_docs(name: str) -> DocumentItem:
    ...


@overload
def get_cmd_docs(cls) -> DocumentItem:
    ...


def get_cmd_docs(cls):
    if not isinstance(cls, str):
        checker = cls.rule.checkers
        first = checker.__iter__().__next__()
        call = first.call
        if hasattr(call, 'cmds'):
            cmds = call.cmds
            cmd_tuple = [x[0] for x in cmds]
        else:
            cmd_tuple = [first.call.regex]

        result = filter(lambda x: DocumentGenerator.commands.get(x), cmd_tuple)
        result = list(result)
        if not result:
            raise Exception('no suitable docs')
        cls = result[0]

    return DocumentGenerator.commands.get(cls)


# 覆盖matcher.Matcher.handle实现依赖注入
# nonebot.matcher.Matcher._handle = nonebot.matcher.Matcher.handle
@classmethod
def hook_handle(cls, parameterless=None):
    wrapper = cls._handle(parameterless)

    def hook_wrapper(raw_handler):
        handler = wrapper(raw_handler)

        async def new_handler(*args, **kwargs):
            print('before call', raw_handler, args, kwargs)
            from ...api.argparser import Jx3Arg, get_args
            arg = AssignableArg(args, kwargs, handler)
            docs = get_cmd_docs(cls)
            if docs.example:  # 检查是否有自动赋值依赖注入
                event = arg.get_assign_by_type(GroupMessageEvent)
                templates = get_args(docs.example, event, method=raw_handler)
                arg.assign_by_type(list[Jx3Arg], templates)
            return await handler(*arg.args, **arg.kwargs)
        return handler
    return hook_wrapper
# TODO 直接使用通用方式赋值
# nonebot.matcher.Matcher.handle = hook_handle
