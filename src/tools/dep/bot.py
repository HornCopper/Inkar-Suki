import sys
import nonebot
import json
import os

from nonebot import get_driver
from nonebot import on, on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.typing import T_State
from tabulate import tabulate
from pathlib import Path
