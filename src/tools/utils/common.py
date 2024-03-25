import re
import time
import datetime

from ..file import write
from ..basic import CLOCK

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


def convert_time(timestamp: int, format: str = "%Y年%m月%d日 %H:%M:%S"):
    if checknumber(timestamp) != False:
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

def relateTime(current, goal):
    current_time = int(datetime.now().timestamp())
    timeGet_int = int(current)
    datetime_1 = datetime.fromtimestamp(timeGet_int)
    datetime_2 = datetime.fromtimestamp(current_time)
    timedelta = datetime_2 - datetime_1
    days = int(timedelta.total_seconds() // 86400)
    hours = int((timedelta.total_seconds() - days*86400) // 3600)
    minutes = int((timedelta.total_seconds() - days*86400 - hours*3600) // 60)
    days = str(days)
    hours = str(hours)
    minutes = str(minutes)
    if len(days) == 1:
        days = "0" + days
    if len(hours) == 1:
        hours = "0" + hours
    if len(minutes) == 1:
        minutes = "0" + minutes
    relateTime = f"{days}天{hours}时{minutes}分前"
    return relateTime

def record_info(record_content: str):
    msg = convert_time(getCurrentTime(), "[%Y-%m-%d %H:%M:%S] "+ record_content)
    write(CLOCK + "/logs/InkarSuki.log", msg)