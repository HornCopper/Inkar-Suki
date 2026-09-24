import re

from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg

from src.utils.command import on_command

from .app import ORIGIN_FRAME, render_haste_image


haste_matcher = on_command(
    "jx3_haste", command_key="加速", aliases={"加速", "急速"},
    priority=5, force_whitespace=True,
)


@haste_matcher.handle()
async def _(args: Message = CommandArg()):
    parts = args.extract_plain_text().split()
    usage = "参考格式：加速 [基础帧数] [附加加速]，例如：加速 48、加速 24 50、加速 24 50U。"
    if len(parts) > 2 or (parts and not re.fullmatch(r"[1-9]\d*", parts[0])):
        await haste_matcher.finish(usage)
    if len(parts) == 2 and not re.fullmatch(r"\d+[Uu]?", parts[1]):
        await haste_matcher.finish(usage)
    origin_frame = int(parts[0]) if parts else ORIGIN_FRAME
    addition_rate = int(parts[1].rstrip("Uu")) if len(parts) == 2 else 0
    unlimited = len(parts) == 2 and parts[1][-1] in "Uu"
    await haste_matcher.finish(await render_haste_image(origin_frame, addition_rate, unlimited))
