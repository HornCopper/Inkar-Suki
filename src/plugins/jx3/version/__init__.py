from nonebot import on_command
from nonebot.params import RawCommand, CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from .api import get_latest_version

version_matcher = on_command("jx3_version", aliases={"版本", "体服版本"}, priority=5, force_whitespace=True)

@version_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg(), cmd: str = RawCommand()):
    if args.extract_plain_text().strip() != "":
        return
    is_exp = "体服" in cmd
    version_name = "体服" if is_exp else "正式服"
    version = await get_latest_version(is_exp)
    msg = f"当前{version_name}最新版本号为：{version}"
    await version_matcher.finish(msg)