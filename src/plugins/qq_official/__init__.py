from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from src.adapters.qq_official import QQCompatBot


identity_matcher = on_command("官号信息", aliases = {"qq身份"}, priority = 5, force_whitespace = True)


@identity_matcher.handle()
async def show_identity(bot: QQCompatBot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text().strip():
        return
    context = "群" if bot.is_group else "单聊上下文"
    await identity_matcher.finish(
        f"QQ 官方机器人\n应用：{bot.app_id}\n用户内部 ID：{bot.raw_user_id}\n{context}内部 ID：{bot.raw_group_id}\n"
        f"当前数据用户 ID：{event.user_id}\n当前数据{context} ID：{event.group_id}\n"
        "负数为本项目内部标识。管理员可通过“匹配个人 -内部ID QQ号”或“匹配群 -内部ID 群号”关联号码；匹配信息由管理员指定，不代表官方返回了真实号码。",
    )
