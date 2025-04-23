from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Arg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from src.utils.database import db
from src.utils.database.classes import PersonalSettings

from .app import Preference

personal_preferences = on_command("偏好", priority=5, force_whitespace=True)

@personal_preferences.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    args = msg.extract_plain_text().strip().split(" ")
    if args == [""]:
        args = []
    if len(args) not in [0, 1, 2]:
        await personal_preferences.finish("格式错误，请参考下面的格式：\n查询目前偏好：偏好\n查询某项偏好：偏好 偏好项\n设置偏好：偏好 偏好项 设定值")
    if len(args) == 0: # 查询
        image = await Preference(event.user_id, "", "").query()
        await personal_preferences.finish(image)
    elif len(args) == 1: # 查询 偏好项
        reply = Preference(event.user_id, args[0], "").get()
        await personal_preferences.finish(reply)
    else:
        reply = Preference(event.user_id, args[0], args[1]).set()
        await personal_preferences.finish(reply)

reset_preferences = on_command("重置偏好", priority=5, force_whitespace=True)

@reset_preferences.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, msg: Message = CommandArg()):
    if msg.extract_plain_text() != "":
        matcher.stop_propagation()
        return
    await reset_preferences.send("确定要重置您的个人偏好吗？如果是，请发送“是”。\n注意：您绑定的角色和偏好会一并丢失。")

@reset_preferences.got("reply")
async def _(event: GroupMessageEvent, reply: Message = Arg()):
    if reply.extract_plain_text() == "是":
        db.delete(PersonalSettings(), "user_id = ?", str(event.user_id))
        await reset_preferences.finish("清除成功！您可以重新开始设置偏好以及绑定角色了！")