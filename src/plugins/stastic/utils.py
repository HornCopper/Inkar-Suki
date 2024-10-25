import time
from datetime import datetime

def get_date_timestamp(date_str: str) -> tuple[int, int]:
    current_year = datetime.now().year
    try:
        start_time_str = f"{current_year}-{date_str} 00:00:00"
        end_time_str = f"{current_year}-{date_str} 23:59:59"
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        today = datetime.now()
        start_time = datetime(today.year, today.month, today.day, 0, 0, 0)
        end_time = datetime(today.year, today.month, today.day, 23, 59, 59)
    start_timestamp = int(time.mktime(start_time.timetuple()))
    end_timestamp = int(time.mktime(end_time.timetuple()))
    return start_timestamp, end_timestamp