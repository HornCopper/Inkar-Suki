from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

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