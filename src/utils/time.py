from datetime import datetime

class Time:
    """
    时间处理对象。
    """
    def __init__(self, time: int = 0):
        """
        初始化时间对象。

        Args:
            time (int): 需要比对的时间戳，不传入则使用当前时间戳。
        """
        time = int(datetime.now().timestamp()) if time == 0 else time
        self.current: int = time

    @property
    def raw_time(self):
        """
        原始时间戳。
        """
        return self.current

    def format(self, form: str = "%Y年%m月%d日 %H:%M:%S"):
        """
        格式化时间。
        
        Args:
            form (str): 时间格式，默认`%Y年%m月%d日 %H:%M:%S`。
        
        Returns:
            formatted_time (str): 格式化时间。
        """
        timestamp = self.current
        if timestamp >= 1000000000000:
            timestamp = int(timestamp / 1000)
        return datetime.fromtimestamp(timestamp).strftime(form)

    def relate(self, time: int = 0) -> str:
        """
        计算相对时间。
        
        Args:
            time (int): 与实例时间进行对比的时间戳。

        Returns:
            relate_time (str): 相对时间（已格式化）。
        """
        start = int(self.current)
        end = int(time)

        start_timestamp = datetime.fromtimestamp(start)
        end_timestamp = datetime.fromtimestamp(end)

        timedelta = end_timestamp - start_timestamp
        total_seconds = abs(int(timedelta.total_seconds()))

        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)

        days = f"{days:02}"
        hours = f"{hours:02}"
        minutes = f"{minutes:02}"

        if start >= end:
            flag = "前"
        else:
            flag = "后"
        relateTime = f"{days}天{hours}时{minutes}分{flag}"
        return relateTime
