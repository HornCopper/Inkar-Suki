from sgtpyutils.logger import logger
try:
    logger.debug(f'load dependence:{__name__}')
except:
    pass
from src.tools.generate import *
from src.constant.jx3 import *
from .jx3apiws import *
from .sf_apiws import *
