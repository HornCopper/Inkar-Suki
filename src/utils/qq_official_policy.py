"""未匹配群号的官方群仅允许运行身份配置入口。"""

from nonebot.matcher import Matcher

_setup_matchers: set[type[Matcher]] = set()


def allow_unmatched_group(matcher: type[Matcher]) -> type[Matcher]:
    _setup_matchers.add(matcher)
    return matcher


def allowed_in_unmatched_group(matcher: Matcher) -> bool:
    return type(matcher) in _setup_matchers
