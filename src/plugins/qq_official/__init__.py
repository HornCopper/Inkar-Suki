from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from src.adapters.qq_official import QQCompatBot
from src.utils.qq_official_policy import allow_unmatched_group


identity_matcher = allow_unmatched_group(
    on_command("官号信息", aliases = {"qq身份"}, priority = 5, force_whitespace = True),
)


@identity_matcher.handle()
async def show_identity(bot: QQCompatBot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text().strip():
        return
    context = "群聊" if bot.is_group else "单聊上下文"
    status = "本群已完成注册！如出现问题请前往音卡官方群聊联系管理员！"
    if bot.is_group and bot.group_id < 0:
        status = "本群尚未完成注册！请发送“官号信息”并将返回的信息发送给机器人管理员完成注册！"
    await identity_matcher.finish(
        f"QQ 官方机器人\n用户 ID：{bot.raw_user_id}\n{context} ID：{bot.raw_group_id}\n"
        f"匹配用户：{event.user_id}\n匹配{context}：{event.group_id}\n"
        f"{status}"
    )
