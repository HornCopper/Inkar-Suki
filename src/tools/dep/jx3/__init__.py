from sgtpyutils.logger import logger
try:
    logger.debug(f'load dependence:{__name__}')
except:
    pass
from src.tools.generate import generate, get_uuid, generate_by_url, stop_playwright
from src.constant.jx3 import *
from .jx3apiws import *
