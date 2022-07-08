import json, sys, nonebot, os
from nonebot import on_command, on_message
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event, Bot, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.log import logger
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
DATA = TOOLS[:TOOLS.find("/tools")]+"/data"
from permission import checker, error
from file import read, write
from http_ import http
from config import Config

unregistered = on_message(block=False,priority=1)
@unregistered.handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    directorys=os.listdir(TOOLS.replace("tools","data"))
    if str(event.group_id) not in directorys:
        matcher.stop_propagation()
    else:
        return
    
register = on_command("register",aliases={"reg"},priority=0)
@register.handle()
async def _(event: GroupMessageEvent):
    if checker(str(event.user_id),8) == False:
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
        write(new_path+"/block.json","[]")
        await register.finish("注册成功！")

flushdata = on_command("flushdata",priority=5)
@flushdata.handle()
async def _(event: Event):
    if checker(str(event.user_id),10) == False:
        await register.finish(error(10))
    directorys=os.listdir("./src/data")
    enable_groups = json.loads(await http.get_url(f"{Config.cqhttp}get_group_list"))
    disabled_groups = []
    for i in enable_groups["data"]:
        if str(i["group_id"]) not in directorys:
            disabled_groups.append(str(i["group_id"]))
    for i in disabled_groups:
        try:
            os.rmdir(DATA+"/"+i)
        except:
            logger.info("删除文件夹"+i+"失败，未知错误。")
    dlt_count = len(disabled_groups)
    await flushdata.finish("好啦，刷新完成！\n删除了"+str(dlt_count)+"个文件夹。")