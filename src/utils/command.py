from typing import Any

from nonebot import on_command as _on_command
from nonebot.log import logger
from nonebot.matcher import Matcher

from src.utils.database import logs_db
from src.utils.database.classes import CommandUsage
from src.utils.time import Time

COMMAND_KEYS: set[str] = set()

def get_command_keys() -> set[str]:
    """返回当前进程内所有参与统计的命令 key。"""
    return COMMAND_KEYS.copy()

def on_command(
    command: str | tuple[str, ...],
    *args: Any,
    command_key: str | None = None,
    **kwargs: Any,
) -> type[Matcher]:
    """注册命令 Matcher，并按 command_key 记录每次调用。"""
    matcher = _on_command(command, *args, **kwargs)

    if command_key is not None:
        COMMAND_KEYS.add(command_key)

        @matcher.handle()
        async def _record_command_usage() -> None:
            try:
                logs_db.save(
                    CommandUsage(
                        command_key = command_key,
                        timestamp = Time().raw_time,
                    ),
                )
            except Exception:
                logger.exception(f"命令调用统计写入失败：{command_key}")

    return matcher
