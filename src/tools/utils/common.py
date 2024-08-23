from typing import Union

from src.tools.file import write, read

import re
import time
import datetime
import pathlib2
import os

tools_path = f"{os.getcwd()}/src/tools"

def get_path(path: str) -> str:
    t = pathlib2.Path(tools_path)
    return t.parent.joinpath(path).__str__()
CLOCK = get_path("clock")

def get_number(number):
    """
    返回参数的数值，默认返回0
    """
    if not checknumber(number):
        return 0
    return int(number)


def get_number_with_default(number) -> tuple[int, bool]:
    """
    返回参数的数值，默认返回0
    如果是默认值，则返回True
    """
    if isinstance(number, str):
        number = number.strip()
    if not checknumber(number):
        return 0, True
    return int(number), False


def checknumber(value):
    """
    检查参数是否是数值
    """
    if value is None:
        return False
    if isinstance(value, str):
        pattern = r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$"
        return bool(re.match(pattern, value))
    if isinstance(value, int):
        return True
    return value.isdecimal()


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


def nodetemp(nickname: str, qqnumber: str, message: str) -> dict:
    return {"type": "node", "data": {"name": nickname, "uin": qqnumber, "content": message}}


def prefix(event, prefix):
    if str(event.raw_message)[0] != prefix:
        return False
    return True

def getCurrentTime():
    return int(datetime.datetime.now().timestamp())

def getRelateTime(current, goal):
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

def record_info(record_content: str):
    msg = convert_time(getCurrentTime(), "[%Y-%m-%d %H:%M:%S] "+ record_content)
    if not isinstance(msg, str):
        return
    raw = read(CLOCK + "/logs/InkarSuki.log")
    msg = raw + "\n" + msg
    write(CLOCK + "/logs/InkarSuki.log", msg)