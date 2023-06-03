import time
from .config import Config
from nonebot import get_driver
from typing import Tuple 
    
#获取配置cd时间
cd = Config.parse_obj(get_driver().config.dict()).whateat_cd
max_count = Config.parse_obj(get_driver().config.dict()).whateat_max


def check_cd(last_time:int) ->Tuple[bool,int,int]:
    #检查cd
    current_time = int(time.time())
    delta_time = current_time - last_time
    if delta_time < cd:
        return False,cd-delta_time,last_time
    else:
        return True,0,current_time
    
    
def check_max(message,user_count:dict) ->Tuple[bool,dict]:
    # 判断是否达到每日最大值
    user_id = message.get_user_id()
    if max_count == 0:
        return False,{}
    if user_id not in user_count:
        user_count[f"{user_id}"] = 0
    if user_count[f"{user_id}"] < max_count:
        user_count[f"{user_id}"] += 1
        return False,user_count
    else:
        return True,user_count
    