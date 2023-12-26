
import nonebot


def __hook_on_command():
    __raw_on_command = nonebot.on_command

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
        return __raw_on_command(cmd, rule, aliases, _depth, force_whitespace, **kwargs)
    nonebot.on_command = __hook_on_command


try:
    __hook_on_command()
except:
    pass
