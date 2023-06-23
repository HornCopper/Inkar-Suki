from sgtpyutils.logger import logger
logger.debug(f'load dependence:{__name__}')
from .bot import *
from .api import *
from .jx3 import *
logger.debug(f'load dependence completed:{__name__}')
