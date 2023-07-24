from nonebot import on, on_command, require
from sgtpyutils.logger import logger
import sys
try:
    if not hasattr(sys.modules[__name__], 'scheduler'):
        require("nonebot_plugin_apscheduler")
        from nonebot_plugin_apscheduler import scheduler
        from apscheduler.triggers.date import DateTrigger  # 一次性触发器
        from apscheduler.triggers.cron import CronTrigger  # 定期触发器
        from apscheduler.triggers.interval import IntervalTrigger  # 间隔触发器
except Exception as ex:
    scheduler = None
    logger.warning(f"加载定时依赖失败:{ex}")
