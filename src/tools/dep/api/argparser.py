from __future__ import annotations
from typing import Any
from typing import overload
import functools
from .config import *

from ..exceptions import *
from ..data_server import *
from src.tools.utils import *
from src.constant.jx3.skilldatalib import *
from sgtpyutils import extensions
from sgtpyutils.logger import logger
from .prompt import *
from ..args import *

logger.debug(f'load dependence:{__name__}')


class Jx3ArgCallback:
    def _convert_school(self, arg_value: str, **kwargs) -> str:
        if not arg_value:
            return None
        return kftosh(arg_value)

    def _convert_kunfu(self, arg_value: str, **kwargs) -> str:
        if not arg_value:
            return None
        return std_kunfu(arg_value)

    def _convert_pvp_mode(self, arg_value: str, **kwargs) -> tuple[str, bool]:
        if arg_value not in ['22', '33', '55']:
            return '22', True
        return arg_value

    def _convert_string(self, arg_value: str, **kwargs) -> tuple[str, bool]:
        if not arg_value:
            return None, True
        return str(arg_value), False

    def _convert_server(self, arg_value: str, event: GroupMessageEvent = None, **kwargs) -> tuple[str, bool]:
        server = server_mapping(arg_value)
        if not server and event:
            server = getGroupServer(event.group_id)
            return server, True
        return server, False

    def _convert_user(self, arg_value: str, event: GroupMessageEvent = None, **kwargs) -> tuple[str, bool]:
        return arg_value  # TODO 根据用户当前绑定的玩家自动选择

    def _convert_number(self, arg_value: str, **kwargs) -> tuple[str, bool]:
        x, is_default = get_number_with_default(arg_value)
        return x, is_default

    def _convert_group_id(self, arg_value: str, **kwargs) -> tuple[str, bool]:
        '''TODO 群有效性判断'''
        x, is_default = self._convert_number(arg_value, **kwargs)
        return x, is_default

    def _convert_bool(self, arg_value: str, **kwargs) -> int:
        if arg_value in {'同意', '可', '真', '好', '批准', '准许'}:
            return True
        if arg_value in {'不同意', '不可', '假', '差', '拒绝', '否决'}:
            return False
        x = get_number(arg_value)
        if x == 0:
            return False
        return True

    def _convert_pageIndex(self, arg_value: str, **kwargs) -> tuple[int, bool]:
        is_default = False
        if arg_value is None:
            return 0, True
        v, page_is_default = self._convert_number(arg_value)
        if not v or v < 0:
            v = 1  # 默认返回第一页
            is_default = True
        return v - 1, is_default  # 输入值从1开始，返回值从0开始

    def _convert_subscribe(self, arg_value: str, **kwargs) -> str:
        return arg_value  # TODO 经允许注册有效的

    def _convert_command(self, arg_value: str, **kwargs) -> str:
        return arg_value  # TODO 经允许注册有效的


class Jx3ArgExt:
    @staticmethod
    def requireToken(method):
        @functools.wraps(method)
        async def wrapper(*args, **kwargs):
            from .config import token
            if not token:
                return [PROMPT_NoToken]
            return await method(*args, **kwargs)
        return wrapper

    @staticmethod
    def requireTicket(method):
        @functools.wraps(method)
        async def wrapper(*args, **kwargs):
            from .config import ticket
            if not ticket:
                return [PROMPT_NoTicket]
            return await method(*args, **kwargs)
        return wrapper


class Jx3Arg(Jx3ArgCallback, Jx3ArgExt):
    callback = {
        Jx3ArgsType.default: Jx3ArgCallback._convert_string,
        Jx3ArgsType.number: Jx3ArgCallback._convert_number,
        Jx3ArgsType.bool: Jx3ArgCallback._convert_bool,
        Jx3ArgsType.pageIndex: Jx3ArgCallback._convert_pageIndex,
        Jx3ArgsType.string: Jx3ArgCallback._convert_string,
        Jx3ArgsType.server: Jx3ArgCallback._convert_server,
        Jx3ArgsType.kunfu: Jx3ArgCallback._convert_kunfu,
        Jx3ArgsType.school: Jx3ArgCallback._convert_school,
        Jx3ArgsType.user: Jx3ArgCallback._convert_user,
        Jx3ArgsType.property: Jx3ArgCallback._convert_string,  # TODO 猜测用户想查的物品
        Jx3ArgsType.pvp_mode: Jx3ArgCallback._convert_pvp_mode,
        Jx3ArgsType.subscribe: Jx3ArgCallback._convert_subscribe,
        Jx3ArgsType.command: Jx3ArgCallback._convert_command,
        Jx3ArgsType.group_id: Jx3ArgCallback._convert_group_id,
        Jx3ArgsType.remark: Jx3ArgCallback._convert_string,
    }

    def __init__(self, arg_type: Jx3ArgsType = Jx3ArgsType.default,  name: str = None, is_optional: bool = Ellipsis, default: any = Ellipsis, alias: str = None) -> None:
        self.arg_type = arg_type
        # 显式设置为可选 或 设置了默认值
        if is_optional is not Ellipsis:
            self.is_optional = is_optional
        else:
            self.is_optional = default is not Ellipsis

        self.name = name or str(arg_type)
        self.default = default
        self.alias = alias

    def data(self, arg_value: str, event: GroupMessageEvent = None) -> tuple[str, bool]:
        '''
        获取当前参数的值，获取失败则返回None
        @return 返回值,是否是默认值
        '''
        callback = self.callback.get(self.arg_type)
        if not callback:
            callback = Jx3ArgCallback._convert_string

        result = callback(self, arg_value, event=event)
        if result is None and self.default != Ellipsis:
            return [self.default, True]  # 没有得到有效值，但设置了默认值

        if isinstance(result, tuple):
            return result
        return [result, False]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'[{self.arg_type.name}]{self.name}(default={self.default})'

    @staticmethod
    def arg_factory(matcher: Matcher, event: GroupMessageEvent) -> list[Any]:
        docs = get_cmd_docs(matcher)
        templates = get_args(docs.example, event, method=docs.name)
        if templates is None:  # 不再继续处理
            matcher.stop_propagation()
        return templates

    def to_dict(self):
        return {
            'name': self.name,
            'arg_type': self.arg_type.name,
            'is_optional': self.is_optional,
            'default': None if self.default is Ellipsis else self.default,
            'alias': self.alias,
        }


@overload
def get_args(raw_input: str, template_args: List[Jx3Arg], event: GroupMessageEvent = None) -> list:
    ...


@overload
def get_args(raw_input: MessageSegment, template_args: List[Jx3Arg], event: GroupMessageEvent = None) -> list:
    ...


@overload
def get_args(template_args: List[Jx3Arg], event: GroupMessageEvent) -> list:
    '''如果没有显式提供内容，则从event中提取'''
    ...


def get_args(arg1, arg2, arg3=None, method=None) -> list:
    if isinstance(arg2, GroupMessageEvent):
        message = convert_to_str(arg2)  # 从事件提取
        event = arg2  # 事件是第二个参数
        template_args = arg1
        return direct_get_args(message, template_args, event, method=method)
    return direct_get_args(arg1, arg2, arg3, method=method)


@DocumentGenerator.record
def direct_get_args(raw_input: str, template_args: List[Jx3Arg], event: GroupMessageEvent = None, method=None) -> list:
    template_len = len(template_args)
    raw_input = raw_input or ''  # 默认传入空参数
    user_args = extensions.list2dict(raw_input.split(' '))
    result = []
    user_index = 0  # 当前用户输入
    template_index = 0  # 被匹配参数
    while template_index < template_len:
        arg_value = user_args.get(user_index)  # 获取当前输入参数
        match_value = template_args[template_index]  # 获取当前待匹配参数
        template_index += 1  # 被匹配位每次+1
        x, is_default = match_value.data(arg_value, event)  # 将待匹配参数转换为数值
        result.append(x)  # 无论是否解析成功都将该位置参数填入
        if x is None or is_default:
            if is_default and not match_value.is_optional:
                return InvalidArgumentException(f'{match_value.name}参数无效')
            continue  # 该参数去匹配下一个参数

        user_index += 1  # 输出参数位成功才+1
    return result
