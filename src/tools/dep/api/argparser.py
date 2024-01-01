from __future__ import annotations
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
from ..args import *
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
    logger.warning(f'message cant convert to str:{msg}')
    return msg


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
            Jx3ArgsType.server: self._convert_server,
            Jx3ArgsType.kunfu: self._convert_kunfu,
            Jx3ArgsType.school: self._convert_school,
        }

    def data(self, arg_value: str, event: GroupMessageEvent = None):
        '''
        获取当前参数的值，获取失败则返回None
        '''
        return self.callback[self.arg_type](arg_value, group_id=event.group_id)

    def _convert_school(self, arg_value: str, **kwargs) -> str:
        if not arg_value:
            return None
        return kftosh(arg_value)

    def _convert_kunfu(self, arg_value: str, **kwargs) -> str:
        if not arg_value:
            return None
        return std_kunfu(arg_value)

    def _convert_string(self, arg_value: str, **kwargs) -> str:
        if not arg_value:
            return None
        return str(arg_value)

    def _convert_server(self, arg_value: str, group_id: str = None, **kwargs) -> str:
        return server_mapping(arg_value, group_id)

    def _convert_number(self, arg_value: str, **kwargs) -> int:
        return get_number(arg_value)

    def _convert_pageIndex(self, arg_value: str, **kwargs) -> int:
        if arg_value is None:
            return arg_value
        v = self._convert_number(arg_value)
        if not v or v < 0:
            v = 0
        return v


def get_args(raw_input: str, template_args: List[Jx3Arg], event: GroupMessageEvent = None) -> Tuple:
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
        x = match_value.data(arg_value, event)  # 将待匹配参数转换为数值
        result.append(x)  # 无论是否解析成功都将该位置参数填入
        if x is None:
            if not match_value.is_optional:
                return InvalidArgumentException(f'{match_value.name}参数无效')
            continue  # 该参数去匹配下一个参数

        user_index += 1  # 输出参数位成功才+1
    return result
