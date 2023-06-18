import nonebot
import sys
import json

from nonebot.adapters.onebot.v11 import MessageSegment as ms
from src.tools.utils import get_api
from src.tools.file import read
from sgtpyutils.logger import logger
from src.tools.dep.bot import *
from src.tools.dep.api import *
from src.tools.dep.path import *
from src.constant.jx3.skilldatalib import aliases

from .achievement import *
from .arena import *
from .bind import *
from .buff import *
from .daily import *
from .dungeon import *
from .exam import *
from .fireworks import *
from .horse import *
from .jxjoy import *
from .matrix import *
from .news import *
from .notice import *
from .other import *
from .pet import *
from .price_account import *
from .price_appearance import *
from .price_gold import *
from .price_goods import *
from .price_wbl import *
from .rank import *
from .recruit import *
from .sandbox import *
from .server import *
from .skill import *
from .subscribe import *
from .task import *
from .user import *
from .venture import *