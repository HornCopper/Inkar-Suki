from sgtpyutils.logger import logger
try:
    logger.debug(f'load dependence:{__name__}')
except:
    pass
from src.constant.jx3 import *
from .jx3apiws import ws_client, Jx3WebSocket, RecvEvent