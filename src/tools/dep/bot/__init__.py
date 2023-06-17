import sys
import nonebot
import json
import os

from nonebot import get_driver
from nonebot import on, on_command
from nonebot.adapters import Message, MessageSegment
from nonebot.params import CommandArg, Arg
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message as obMessage
from nonebot.adapters.onebot.v11.message import Message as v11Message
from nonebot.adapters.onebot.v11.event import Anonymous, Sender, Reply
from nonebot.typing import T_State
from tabulate import tabulate
from pathlib import Path
from nonebot.message import handle_event
from sgtpyutils.logger import logger
from nonebot import get_bots