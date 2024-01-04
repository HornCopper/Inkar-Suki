from sgtpyutils.functools import AssignableArg
import functools

from nonebot.matcher import Matcher

def use_auto_assign_args(command_name, matcher):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            arg = AssignableArg(args, kwargs)
            method(*arg.args, **arg.kwargs)
        return wrapper
    return decorator
