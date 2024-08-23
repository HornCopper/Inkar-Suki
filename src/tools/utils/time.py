from typing import Union

from src.tools.utils.num import checknumber

import time
import datetime

def convert_time(timestamp: int, format: str = "%Y年%m月%d日 %H:%M:%S") -> Union[str, bool]:
    if checknumber(timestamp):
        try:
            timestamp = int(timestamp)
        except:
            return False
    """
    时间转换，自适应时间长度。
    """
    if len(str(timestamp)) == 13:
        time_local = time.localtime(timestamp / 1000)
    elif len(str(timestamp)) == 10:
        time_local = time.localtime(timestamp)
    else:
        class TimeLengthError(OSError):
            ...
        raise TimeLengthError("Length of timestamp cannot be approved!")
    dt = time.strftime(format, time_local)
    return dt

def get_current_time():
    return int(datetime.datetime.now().timestamp())

def get_relate_time(current, goal):
    current_time = int(current)
    timeGet_int = int(goal)
    datetime_1 = datetime.datetime.fromtimestamp(current_time)
    datetime_2 = datetime.datetime.fromtimestamp(timeGet_int)
    timedelta = datetime_2 - datetime_1
    days = int(abs(timedelta.total_seconds()) // 86400)
    hours = int((abs(timedelta.total_seconds()) - days*86400) // 3600)
    minutes = int((abs(timedelta.total_seconds()) - days*86400 - hours*3600) // 60)
    days = str(days)
    hours = str(hours)
    minutes = str(minutes)
    if len(days) == 1:
        days = "0" + days
    if len(hours) == 1:
        hours = "0" + hours
    if len(minutes) == 1:
        minutes = "0" + minutes
    if current_time >= timeGet_int:
        flag = "前"
        msg = f"{days}天{hours}时{minutes}分"
    else:
        flag = "后"
        msg = f"{days}天{hours}时{minutes}分"[1:]
    relateTime = msg + flag
    return relateTime