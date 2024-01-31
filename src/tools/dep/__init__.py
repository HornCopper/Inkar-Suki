from nonebot.log import logger
logger.debug(f"load dependence:{__name__}")
from .bot import *
from .jx3 import *
from .api import *
from .GroupStatistics import *
logger.debug(f"load dependence completed:{__name__}")
