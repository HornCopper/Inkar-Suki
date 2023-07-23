from __future__ import annotations
from nonebot.adapters.onebot.v11.message import Message as v11Message
from nonebot.adapters import Message, MessageSegment
from enum import IntEnum
from typing import List, Literal, Tuple
from ..exceptions import *
from ..data_server import *
from src.tools.utils import *
from sgtpyutils import extensions
from sgtpyutils.logger import logger
logger.debug(f'load dependence:{__name__}')


def convert_to_str(msg: MessageSegment):
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
    logger.warn(f'message cant convert to str:{msg}')
    return msg


class Jx3ArgsType(IntEnum):
    default = 0
    string = 1
    number = 2
    server = 3
    pageIndex = 4
    pageSize = 5


class Jx3Arg:
    def __init__(self, arg_type: Jx3ArgsType = Jx3ArgsType.default,  name: str = None, is_optional: bool = True) -> None:
        self.arg_type = arg_type
        self.is_optional = is_optional
        self.name = name or str(arg_type)

        self.callback = {
            Jx3ArgsType.default: self._convert_string,
            Jx3ArgsType.number: self._convert_number,
            Jx3ArgsType.pageIndex: self._convert_pageIndex,
            Jx3ArgsType.string: self._convert_string,
            Jx3ArgsType.server: self._convert_server
        }

    def data(self, arg_value: str):
        '''
        获取当前参数的值，获取失败则返回None
        '''
        return self.callback[self.arg_type](arg_value)

    def _convert_string(self, arg_value: str) -> str:
        if not arg_value:
            return None
        return str(arg_value)

    def _convert_server(self, arg_value: str) -> str:
        return server_mapping(arg_value)

    def _convert_number(self, arg_value: str) -> int:
        return get_number(arg_value)

    def _convert_pageIndex(self, arg_value: str) -> int:
        if arg_value is None:
            return arg_value
        v = self._convert_number(arg_value)
        if not v or v < 0:
            v = 0
        return v


def get_args(raw_input: str, template_args: List[Jx3Arg]) -> Tuple:
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
        x = match_value.data(arg_value)  # 将待匹配参数转换为数值
        result.append(x)  # 无论是否解析成功都将该位置参数填入
        if x is None:
            if not match_value.is_optional:
                return InvalidArgumentException(f'{match_value.name}参数无效')
            continue  # 该参数去匹配下一个参数

        user_index += 1  # 输出参数位成功才+1
    return result
