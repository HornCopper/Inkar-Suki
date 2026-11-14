from nonebot.adapters.onebot.v11 import (
    Message,
    GroupMessageEvent,
)
from nonebot.params import CommandArg

from src.utils.command import on_command
from src.utils.jx3api import jx3api_get

from .image import get_image

announce_matcher = on_command(
    "jx3_announce",
    command_key = "公告",
    aliases = {"维护公告", "更新公告", "公告", "更新"},
    force_whitespace = True,
    priority = 5,
)

@announce_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取维护公告的图片：

    Example：-维护公告
    """
    if args.extract_plain_text() != "":
        return
    img = await get_image()
    await announce_matcher.finish(img)

beta_announce_matcher = on_command(
    "jx3_beta_announce",
    command_key = "公告",
    aliases = {"体服公告", "体服更新"},
    priority = 5,
    force_whitespace = True,
)

@beta_announce_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取体服维护公告。
    """
    if args.extract_plain_text() != "":
        return
    img = await get_image(ver = "latest_exp")
    await beta_announce_matcher.finish(img)

skill_change_matcher = on_command(
    "jx3_skillrecord",
    command_key = "技改",
    aliases = {"技改", "技改记录"},
    priority = 5,
    force_whitespace = True,
)

@skill_change_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    else:
        url = "/skill/rework"
        data = await jx3api_get(url)
        if data["code"] != 200:
            await skill_change_matcher.finish(data["msg"] or "技改查询失败，请稍后重试！")
        msg = ""
        for d in data["data"][0:4]:
            title = d["title"]
            url = d["url"]
            msg += f"\n标题：{title}\n链接：{url}"
        await skill_change_matcher.finish(msg.strip())
