from nonebot.log import logger
try:
    logger.debug(f"load dependence:{__name__}")
except Exception as _:
    pass
from src.tools.generate import *
from src.constant.jx3 import *
from .jx3apiws import *
try:
    from .tuilan import *
except:
    pass