from functools import wraps
from typing import Callable
from nonebot.log import logger
# from nonebot.adapters.onebot.v11 import Message

from src.config import Config
from src.const.prompts import PROMPT
from src.utils.exceptions import ConfigurationException

import time
import asyncio

# def require_argument(require_non_empty: bool = True):
#     """
#     **尚未决定是否使用该装饰器。**

#     ~~装饰NoneBot响应器装饰的函数，检查是否需要参数。~~
#     """
#     def decorator(func):
#         @wraps(func)
#         async def wrapper(*args, **kwargs):
#             message_arg = None
#             for arg in args:
#                 if isinstance(arg, Message):
#                     message_arg = arg
#                     break
#             if message_arg is None:
#                 for arg in kwargs.values():
#                     if isinstance(arg, Message):
#                         message_arg = arg
#                         break
            
#             if (require_non_empty and 
#                 message_arg and 
#                 message_arg.extract_plain_text().strip() == ""):
#                 return
#             elif (not require_non_empty and 
#                   (message_arg is None or 
#                    message_arg.extract_plain_text().strip() != "")):
#                 return

#             return await func(*args, **kwargs)
        
#         return wrapper
#     return decorator

def ticket_required(func) -> Callable:
    """
    检查并传入`Ticket`。
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        ticket = Config.jx3.api.ticket
        return func(ticket=ticket, *args, **kwargs)
    return wrapper

def token_required(func) -> Callable:
    """
    检查并传入`Token`。
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = Config.jx3.api.token
        if token == "":
            return PROMPT.NoToken
        if token == "" and Config.jx3.api.enable:
            raise ConfigurationException("Cannot enable `JX3API` with a null `token`!")
        return func(token = token, *args, **kwargs)
    return wrapper

def time_record(func):
    """
    对同步和异步函数执行时间进行计时的装饰器。
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        time_start = time.time()
        result = await func(*args, **kwargs)
        time_end = time.time()
        logger.opt(colors=True).info(f"<green>{func.__name__} running  completed, {time_end - time_start:.6f}s spent.</green>")
        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        time_start = time.time()
        result = func(*args, **kwargs)
        time_end = time.time()
        logger.opt(colors=True).info(f"<green>{func.__name__} running  completed, {time_end - time_start:.6f}s spent.</green>")
        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper