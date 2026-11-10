"""在官方消息的规则检查前排除不可能匹配的普通命令。"""

from functools import wraps

from nonebot.adapters import Bot
from nonebot.matcher import Matcher
from nonebot.rule import CommandRule, ShellCommandRule

_installed = False


def install_command_prefilter(proxy_type: type[Bot]) -> None:
    global _installed
    if _installed:
        return
    original = Matcher.check_rule.__func__

    @wraps(original)
    async def check_rule(cls, bot, event, state, stack=None, dependency_cache=None):
        prefix = state.get("_prefix")
        if isinstance(bot, proxy_type) and isinstance(prefix, dict) and "command" in prefix:
            command = prefix["command"]
            for checker in cls.rule.checkers:
                rule = checker.call
                # Rule 中的检查器是 AND；只提前判断内置命令规则的必要条件。
                # 子类、自定义规则及 Alconna 仍交给原流程，匹配命令保留空白、参数等检查。
                if type(rule) in (CommandRule, ShellCommandRule) and command not in rule.cmds:
                    return False
        return await original(cls, bot, event, state, stack, dependency_cache)

    Matcher.check_rule = classmethod(check_rule)
    _installed = True
