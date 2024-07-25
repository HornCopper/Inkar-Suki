from .. import *

try:
    from .jx3 import gen_ts, gen_xsk, format_body, dungeon_sign
except:
    pass

import json
import os
import sys
import re

from src.constant.jx3 import *
from src.tools.generate import get_uuid, generate
from src.tools.permission import checker, error

from .jx3 import *
from .data_server import server_mapping, getGroupServer, Zone_mapping
from .message_process import *
from .group_opeator import *
from .spark import *
from ..data import *

from nonebot.adapters.onebot.v11 import MessageSegment as ms, Event, GroupMessageEvent, Bot
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg, Received
from nonebot import on_command, on, on_regex, on_request, on_notice, on_message
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot import get_driver

from typing import List, Union, Any


PROMPT_NoToken = "唔……该音卡实例没有填写JX3API的token，数据获取失败，请联系机器人主人！"
PROMPT_ServerNotExist = "唔……没有找到服务器参数，群聊似乎也没有绑定服务器哦，要不绑定试试呢？"
PROMPT_ArgumentInvalid = "唔……参数数量有误，请检查后重试~"
PROMPT_NoTicket = "唔……该音卡实例没有填写推栏的Ticket，数据获取失败，请联系机器人主人！"
PROMPT_ServerInvalid = "唔……服务器输入有误！"
PROMPT_ArgumentCountInvalid = "唔……参数数量有误，请检查后重试！"
PROMPT_NumberInvalid = "唔……输入的不是数字哦，取消搜索。"
PROMPT_InvalidToken = "唔……该音卡实例的JX3API的token无效，请联系机器人主人！"
PROMPT_NumberNotExist = "唔……输入的数字不在范围内哦，请检查后重试！"
PROMPT_PlayerNotExist = "唔……玩家不存在哦，请检查后重试！"

token = Config.jx3.api.token
ticket = Config.jx3.api.ticket
bot = "Inkar-Suki"
device_id = ticket.split("::")[-1]