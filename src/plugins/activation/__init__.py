from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from src.utils.analyze import check_number
from src.utils.permission import check_permission

from .app import get_expire_at, update_expire_time

expire_at = on_command("到期时间", rule=to_me(), priority=5)

@expire_at.handle()
async def _(event: GroupMessageEvent):
    expire_msg = get_expire_at(event.group_id)
    msg = f"本群（{event.group_id}）授权情况如下：\n{expire_msg}"
    await expire_at.finish(msg)

update_activation = on_command("授权", rule=to_me(), priority=5)

@update_activation.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    days = args.extract_plain_text()
    if not check_number(days):
        await update_activation.finish("请使用“授权 天数”，确保天数为数字！")
    if days == "-1" and not check_permission(event.user_id, 10):
        await update_activation.finish("权限不足，仅机器人管理员可设置永久授权！")
    msg = update_expire_time(event.group_id, int(days))
    await update_activation.finish(msg)