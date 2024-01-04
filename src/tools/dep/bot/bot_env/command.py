
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from sgtpyutils.functools import AssignableArg
import functools
import nonebot
from sgtpyutils.logger import logger
from .document import DocumentGenerator

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
    command_item = nonebot._on_regex(f'{pattern} ', flags, rule, _depth)
    return command_item


nonebot._on_regex = nonebot.on_regex  # 初始化
nonebot.on_regex = __hook_on_regex

# 覆盖matcher.Matcher.handle实现依赖注入
nonebot.matcher.Matcher._handle = nonebot.matcher.Matcher.handle


def get_cmd_docs(cls):
    checker = cls.rule.checkers
    first = checker.__iter__().__next__()
    cmds = first.call.cmds
    cmd_tuple = [x[0] for x in cmds]

    result = filter(lambda x: DocumentGenerator.commands.get(x), cmd_tuple)
    result = list(result)
    if not result:
        raise Exception('no suitable docs')
    return DocumentGenerator.commands.get(result[0])


@classmethod
def hook_handle(cls, parameterless=None):
    wrapper = cls._handle

    def hook_wrapper(method):
        wrap_func = wrapper(parameterless)(method)

        @functools.wraps(method)
        def before_call(*args, **kwargs):
            from ...api.argparser import Jx3Arg, get_args
            arg = AssignableArg(args, kwargs, wrap_func)
            docs = get_cmd_docs(cls)
            if docs.example:  # 检查是否有自动赋值依赖注入
                event = arg.get_assign_by_type(GroupMessageEvent)
                templates = get_args(docs.example, event, method=method)
                arg.assign_by_type(list[Jx3Arg], templates)
            return wrap_func(*arg.args, **arg.kwargs)
        return before_call
    return hook_wrapper


# TODO 直接使用通用方式赋值
nonebot.matcher.Matcher.handle = hook_handle
