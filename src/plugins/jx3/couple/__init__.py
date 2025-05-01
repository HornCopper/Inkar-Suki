from datetime import datetime

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg

from src.const.prompts import PROMPT
from src.utils.analyze import check_number
from src.utils.time import Time

from .app import (
    bind_affection,
    delete_affection,
    generate_affection_image
)

bind_affection_matcher = on_command("jx3_affbind", aliases={"绑定情缘"}, force_whitespace=True, priority=5)

@bind_affection_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [3, 4]:
        await bind_affection_matcher.finish("绑定失败！请参考下面的命令格式：\n绑定情缘 自己ID 对方ID 对方QQ 时间(可不填)")
    self_name = arg[0]
    self_qq = event.user_id
    other_name = arg[1]
    other_qq = int(arg[2])
    custom_time = arg[3] if len(arg) == 4 else Time().format("%Y-%m-%d")
    if not isinstance(custom_time, str):
        return
    timestamp = 0
    try:
        timestamp = int(datetime.strptime(custom_time, "%Y年%m月%d日").timestamp())
    except ValueError:
        try:
            timestamp = int(datetime.strptime(custom_time, "%Y-%m-%d").timestamp())
        except ValueError:
            await bind_affection_matcher.finish(PROMPT.AffectionFormatInvalid)
    if not check_number(other_qq):
        await bind_affection_matcher.finish(PROMPT.AffectionUINInvalid)
    ans = await bind_affection(self_qq, self_name, other_qq, other_name, event.group_id, timestamp)
    await bind_affection_matcher.finish(ans[0])

delete_affection_matcher = on_command("jx3_affdl", aliases={"解除情缘"}, force_whitespace=True, priority=5)

@delete_affection_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    self_id = event.user_id
    ans = await delete_affection(self_id)
    if not isinstance(ans, list):
        return
    await delete_affection_matcher.finish(ans[0])

affection_crt_matcher = on_command("jx3_affcrt", aliases={"查看情缘证书"}, force_whitespace=True, priority=5)

@affection_crt_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    img = await generate_affection_image(event.user_id)
    await affection_crt_matcher.finish(img)