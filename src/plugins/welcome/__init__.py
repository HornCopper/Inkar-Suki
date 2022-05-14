import sys

from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot import on_notice, on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, NoticeEvent, Event
from nonebot.params import CommandArg

import nonebot
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
from permission import checker, error
from file import read, write

welcome = on_notice(priority=5)


@welcome.handle()
async def _(bot: Bot, event: NoticeEvent):
    if event.notice_type == "group_increase":
        obj = event.user_id
        group = event.group_id
        msg = ms.at(obj) + read(TOOLS+"/welcome.txt")
        await bot.call_api("send_group_msg",group_id=group, message=msg)
    elif event.notice_type == "group_decrease":
        who = event.user_id
        group = event.group_id
        if group == 458416873:
            return
        info = await bot.call_api("get_stranger_info", user_id=who)
        name = info["nickname"]
        msg = f"唔……成员{name}({who})离开了咱们群哦~"
        await bot.call_api("send_group_msg",group_id=group, message=msg)
    
welcome_msg_edit = on_command("welcome_msg_edit",aliases={"wme"},priority=5)

@welcome_msg_edit.handle()
async def __(event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),5) == False:
        await welcome_msg_edit.finish(error(5))
    msg = args.extract_plain_text()
    if msg:
        write(TOOLS+"/welcome.txt", msg)
        await welcome_msg_edit.finish("喵~已设置入群欢迎！")
    else:
        await welcome_msg_edit.finish("您输入了什么？")