from __future__ import annotations
from typing import overload
import functools
from .config import *
from nonebot.adapters.onebot.v11.message import Message as v11Message
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters import Message, MessageSegment
from typing import List, Literal, Tuple
from ..exceptions import *
from ..data_server import *
from src.tools.utils import *
from src.constant.jx3.skilldatalib import *
from sgtpyutils import extensions
from sgtpyutils.logger import logger
from .prompt import *
from ..args import *
import inspect

logger.debug(f'load dependence:{__name__}')


def convert_to_str(msg: MessageSegment):
    if isinstance(msg, GroupMessageEvent):
        x = msg.get_message().extract_plain_text()
        msg = str.join(' ', x.split(' ')[1:])  # 将命令去除
    if isinstance(msg, MessageSegment):
        msg = msg.data
    if isinstance(msg, v11Message):
        msg = str(msg)
        pass
    if isinstance(msg, dict):
        import json
        msg = json.dumps(msg, ensure_ascii=False)

    if isinstance(msg, str):
        return msg
    logger.warning(f'message cant convert to str:{msg}')
    return msg


class Jx3ArgCallback:
    def _convert_school(self, arg_value: str, **kwargs) -> str:
        if not arg_value:
            return None
        return kftosh(arg_value)

    def _convert_kunfu(self, arg_value: str, **kwargs) -> str:
        if not arg_value:
            return None
        return std_kunfu(arg_value)

    def _convert_pvp_mode(self, arg_value: str, **kwargs) -> str:
        if not arg_value in ['22', '33', '55']:
            return '22'
        return arg_value

    def _convert_string(self, arg_value: str, **kwargs) -> str:
        if not arg_value:
            return None
        return str(arg_value)

    def _convert_server(self, arg_value: str, event: GroupMessageEvent = None, **kwargs) -> tuple[str, bool]:
        server = server_mapping(arg_value)
        if not server and event:
            server = getGroupServer(event.group_id)
            return server, True
        return server, False

    def _convert_user(self, arg_value: str, event: GroupMessageEvent = None, **kwargs) -> tuple[str, bool]:
        return arg_value  # TODO 根据用户当前绑定的玩家自动选择

    def _convert_number(self, arg_value: str, **kwargs) -> int:
        return get_number(arg_value)

    def _convert_pageIndex(self, arg_value: str, **kwargs) -> int:
        if arg_value is None:
            return arg_value
        v = self._convert_number(arg_value)
        if not v or v < 0:
            v = 0
        return v


class Jx3ArgExt:
    @staticmethod
    def requireToken(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            if not token:
                return [PROMPT_NoToken]
            return method(*args, **kwargs)
        return wrapper

    @staticmethod
    def requireTicket(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            if not ticket:
                return [PROMPT_NoTicket]
            return method(*args, **kwargs)
        return wrapper


class Jx3Arg(Jx3ArgCallback, Jx3ArgExt):
    callback = {
        Jx3ArgsType.default: Jx3ArgCallback._convert_string,
        Jx3ArgsType.number: Jx3ArgCallback._convert_number,
        Jx3ArgsType.pageIndex: Jx3ArgCallback._convert_pageIndex,
        Jx3ArgsType.string: Jx3ArgCallback._convert_string,
        Jx3ArgsType.server: Jx3ArgCallback._convert_server,
        Jx3ArgsType.kunfu: Jx3ArgCallback._convert_kunfu,
        Jx3ArgsType.school: Jx3ArgCallback._convert_school,
        Jx3ArgsType.user: Jx3ArgCallback._convert_user,
        Jx3ArgsType.property: Jx3ArgCallback._convert_string,  # TODO 猜测用户想查的物品
        Jx3ArgsType.pvp_mode: Jx3ArgCallback._convert_pvp_mode,
    }

    def __init__(self, arg_type: Jx3ArgsType = Jx3ArgsType.default,  name: str = None, is_optional: bool = True, default: any = None) -> None:
        self.arg_type = arg_type
        self.is_optional = default or is_optional  # 显式设置为可选 或 设置了默认值
        self.name = name or str(arg_type)
        self.default = default

    def data(self, arg_value: str, event: GroupMessageEvent = None) -> tuple[str, bool]:
        '''
        获取当前参数的值，获取失败则返回None
        @return 返回值,是否是默认值
        '''
        callback = self.callback[self.arg_type]
        result = callback(self, arg_value, event=event)
        if result is None and self.default:
            return [self.default, True]  # 设置了默认值

        if isinstance(result, tuple):
            return result
        return [result, False]


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


def get_args(arg1, arg2, arg3=None) -> list:
    if isinstance(arg2, GroupMessageEvent):
        message = convert_to_str(arg2)  # 从事件提取
        event = arg2  # 事件是第二个参数
        template_args = arg1
        return direct_get_args(message, template_args, event)
    return direct_get_args(arg1, arg2, arg3)


def direct_get_args(raw_input: str, template_args: List[Jx3Arg], event: GroupMessageEvent = None) -> list:
    raw_input = convert_to_str(raw_input)
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

    caller_name = inspect.stack()[2][3]  # 2为往前2层，3为函数名称
    log = {
        'name': caller_name,
        'args': result,
        'raw': raw_input,
        'group': event.group_id,
        'user': event.user_id,
    }
    logger.debug(f'func_called:{log}')
    return result
