from nonebot import on, on_command, require
from sgtpyutils.logger import logger
import sys
try:
    if not hasattr(sys.modules[__name__], 'scheduler'):
        require("nonebot_plugin_apscheduler")
        from nonebot_plugin_apscheduler import scheduler
except Exception as ex:
    scheduler = None
    logger.warning(f"加载定时依赖失败:{ex}")