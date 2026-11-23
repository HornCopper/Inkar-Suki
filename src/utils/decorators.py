from functools import wraps
from typing import Callable
from nonebot.log import logger

from src.config import Config
from src.const.prompts import PROMPT

import inspect
import time
import asyncio

def ticket_required(func) -> Callable:
    """
    检查并传入`Ticket`，同时支持同步和异步函数。
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        ticket = Config.jx3.api.ticket

        # 检查是否为异步函数
        if inspect.iscoroutinefunction(func):

            async def async_wrapper(*args, **kwargs):
                return await func(ticket = ticket, *args, **kwargs)

            return async_wrapper(*args, **kwargs)
        else:
            return func(ticket = ticket, *args, **kwargs)

    return wrapper

def token_required(func) -> Callable:
    """
    检查并传入`Token`，同时支持同步和异步函数。
    """

    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            token = Config.jx3.api.token.strip() or Config.jx3.api.token_v2.strip()
            if not token:
                return PROMPT.NoToken
            return await func(*args, token = token, **kwargs)

        return async_wrapper

    @wraps(func)
    def wrapper(*args, **kwargs):
        token = Config.jx3.api.token.strip() or Config.jx3.api.token_v2.strip()
        if not token:
            return PROMPT.NoToken
        return func(*args, token = token, **kwargs)

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
        logger.opt(
            colors = True,
        ).success(
            f"<green>{func.__name__} running  completed, {time_end - time_start:.6f}s spent.</green>",
        )
        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        time_start = time.time()
        result = func(*args, **kwargs)
        time_end = time.time()
        logger.opt(
            colors = True,
        ).success(
            f"<green>{func.__name__} running  completed, {time_end - time_start:.6f}s spent.</green>",
        )
        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
