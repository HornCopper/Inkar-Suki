import re
import time


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
