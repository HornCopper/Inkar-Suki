from nonebot import on_command
from nonebot.params import RawCommand
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .api import get_latest_version

VersionMatcher = on_command("jx3_version", aliases={"版本", "体服版本"})

@VersionMatcher.handle()
async def _(event: GroupMessageEvent, cmd: str = RawCommand()):
    is_exp = "体服" in cmd
    version_name = "体服" if is_exp else "正式服"
    version = await get_latest_version(is_exp)
    msg = f"当前{version_name}最新版本号为：{version}"
    await VersionMatcher.finish(msg)