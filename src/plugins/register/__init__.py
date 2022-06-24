import json, sys, nonebot, os
from nonebot import on_command, on_message
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event, Bot, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.log import logger
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
from permission import checker, error
from file import read, write

unregistered = on_message(block=False,priority=1)
@unregistered.handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    directorys=os.listdir("./src/data")
    if str(event.group_id) not in directorys:
        matcher.stop_propagation()
    else:
        return
    
register = on_command("register",block=False,priority=0)
@register.handle()
async def _(event: GroupMessageEvent):
    if checker(str(event.user_id),8):
        await register.finish(error(8))
    group = str(event.group_id)
    directorys=os.listdir("./src/data")
    if group in directorys:
        await register.finish("已注册，无需再次注册哦~")
    else:
        new_path = "./src/data/"+group
        os.mkdir(new_path)
        write(new_path+"/webhook.json","[]")
        write(new_path+"/marry.json","[]")
        write(new_path+"/welcome.txt","欢迎入群！")
        write(new_path+"/banword.json","[]")
        await register.finish("注册成功！")
