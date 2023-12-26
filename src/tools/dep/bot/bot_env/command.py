
import nonebot


def __start_hook_on_command():
    def __hook_on_command(
        cmd: nonebot.Union[str, nonebot.Tuple[str, ...]],
        rule: nonebot.Optional[nonebot.Union[nonebot.Rule, nonebot.T_RuleChecker]] = None,
        aliases: nonebot.Optional[nonebot.Set[nonebot.Union[str,
                                                            nonebot.Tuple[str, ...]]]] = None,
        force_whitespace: nonebot.Optional[nonebot.Union[str, bool]] = None,
        _depth: int = 0,
        **kwargs,
    ) -> nonebot.Type[nonebot.Matcher]:
        force_whitespace = ' '
        return nonebot._on_command(cmd, rule, aliases, _depth, force_whitespace, **kwargs)
    nonebot._on_command = __hook_on_command # 初始化
    nonebot._on_command.__code__ = nonebot.on_command.__code__ # 保存原始代码

    nonebot.on_command.__code__ = __hook_on_command.__code__ # 覆盖原始代码


try:
    __start_hook_on_command()
except:
    pass
