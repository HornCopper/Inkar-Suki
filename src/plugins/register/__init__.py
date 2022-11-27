import json
import sys
import nonebot
import os

from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Event, Bot, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.log import logger

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
DATA = TOOLS[:-5] + "data"

from permission import checker, error
from file import read, write
from config import Config
from utils import get_url

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
        new_path = "./src/data/" + group
        os.mkdir(new_path)
        write(new_path + "/jx3group.json","{\"group\":\"" + str(event.group_id) + "\",\"server\":\"\",\"leader\":\"\",\"leaders\":[],\"name\":\"\",\"status\":false}")
        write(new_path + "/webhook.json","[]")
        write(new_path + "/marry.json","[]")
        write(new_path + "/welcome.txt","欢迎入群！")
        write(new_path + "/banword.json","[]")
        write(new_path + "/opening.json","[]")
        write(new_path + "/wiki.json","{\"startwiki\":\"\",\"interwiki\":[]}")
        write(new_path + "/arcaea.json","{}")
        write(new_path + "/record.json","[]")
        await register.finish("注册成功！")

flushdata = on_command("flushdata",priority=5)
@flushdata.handle()
async def _(event: Event):
    if checker(str(event.user_id),10) == False:
        await register.finish(error(10))
    directorys=os.listdir(DATA)
    groups = json.loads(await get_url(f"{Config.cqhttp}get_group_list"))
    enable_group = []
    for i in groups["data"]:
        enable_group.append(str(i["group_id"]))
    disabled_groups = []
    for i in directorys:
        if i not in enable_group:
            disabled_groups.append(i)
    for i in disabled_groups:
        try:
            os.remove(DATA + "/" + i + "/jx3group.json")
            os.remove(DATA + "/" + i + "/webhook.json")
            os.remove(DATA + "/" + i + "/marry.json")
            os.remove(DATA + "/" + i + "/welcome.txt")
            os.remove(DATA + "/" + i + "/banword.json")
            os.remove(DATA + "/" + i + "/wiki.json")
            os.remove(DATA + "/" + i + "/opening.json")
            os.remove(DATA + "/" + i + "/arcaea.json")
            os.remove(DATA + "/" + i + "/record.json")
            nnl = json.loads(read(TOOLS + "/nnl.json"))
            for a in nnl:
                if a == i:
                    nnl.remove(a)
            subscribe = json.loads(read(TOOLS + "/subscribe.json"))
            for a in subscribe:
                if a == i:
                    subscribe.remove(a)
            write(TOOLS + "/nnl.json", nnl)
            write(TOOLS + "/subscribe.json", subscribe)
            os.rmdir(DATA + "/"+i)
        except:
            logger.info("删除文件夹" + i + "失败，未知错误。")
    dlt_count = len(disabled_groups)
    await flushdata.finish("好啦，刷新完成！\n删除了" + str(dlt_count) + "个文件夹。")

leave = on_command("leave",priority=5)
@leave.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if checker(str(event.user_id),8) == False:
        await leave.finish(error(8))
    groups = os.listdir(DATA)
    group = str(event.group_id)
    if group in groups:
        try:
            os.remove(DATA + "/" + group + "/jx3group.json")
            os.remove(DATA + "/" + group + "/webhook.json")
            os.remove(DATA + "/" + group + "/marry.json")
            os.remove(DATA + "/" + group + "/welcome.txt")
            os.remove(DATA + "/" + group + "/banword.json")
            os.remove(DATA + "/" + group + "/record.json")
            os.remove(DATA + "/" + group + "/wiki.json")
            os.remove(DATA + "/" + group + "/opening.json")
            os.remove(DATA + "/" + group + "/arcaea.json")
            nnl = json.loads(read(TOOLS + "/nnl.json"))
            for a in nnl:
                if a == group:
                    nnl.remove(a)
            subscribe = json.loads(read(TOOLS + "/subscribe.json"))
            for a in subscribe:
                if a == group:
                    subscribe.remove(a)
            write(TOOLS + "/nnl.json", nnl)
            write(TOOLS + "/subscribe.json", subscribe)
            os.rmdir(DATA + "/" + group)
        except:
            logger.info("删除文件夹"+group+"失败，未知错误。")
    await leave.send("已清除本群数据，正在退出群聊~")
    await bot.call_api("set_group_leave",group_id=event.group_id)

cleardata = on_command("cleardata",priority=5)
@cleardata.handle()
async def _(event: GroupMessageEvent):
    if checker(str(event.user_id),9) == False:
        await cleardata.finish(error(9))
    groups = os.listdir(DATA)
    group = str(event.group_id)
    if group in groups:
        try:
            os.remove(DATA + "/" + group + "/jx3group.json")
            os.remove(DATA + "/" + group + "/webhook.json")
            os.remove(DATA + "/" + group + "/marry.json")
            os.remove(DATA + "/" + group + "/welcome.txt")
            os.remove(DATA + "/" + group + "/opening.json")
            os.remove(DATA + "/" + group + "/banword.json")
            os.remove(DATA + "/" + group + "/record.json")
            os.remove(DATA + "/" + group + "/wiki.json")
            os.remove(DATA + "/" + group + "/arcaea.json")
            nnl = json.loads(read(TOOLS + "/nnl.json"))
            for a in nnl:
                if a == group:
                    nnl.remove(a)
            subscribe = json.loads(read(TOOLS + "/subscribe.json"))
            for a in subscribe:
                if a == group:
                    subscribe.remove(a)
            write(TOOLS + "/nnl.json", nnl)
            write(TOOLS + "/subscribe.json", subscribe)
            os.rmdir(DATA + "/" + group)
        except:
            logger.info("删除文件夹"+group+"失败，未知错误。")
    await cleardata.finish("已清除本群数据。")

clear = on_command("clear",priority=5)
@clear.handle()
async def _(event: GroupMessageEvent):
    if checker(str(event.user_id),10) == False:
        await clear.finish(error(10))
    groups = os.listdir(DATA)
    for i in groups:
        try:
            os.remove(DATA + "/" + i + "/jx3group.json")
            os.remove(DATA + "/" + i + "/webhook.json")
            os.remove(DATA + "/" + i + "/marry.json")
            os.remove(DATA + "/" + i + "/welcome.txt")
            os.remove(DATA + "/" + i + "/banword.json")
            os.remove(DATA + "/" + i + "/record.json")
            os.remove(DATA + "/" + i + "/wiki.json")
            os.remove(DATA + "/" + i + "/opening.json")
            os.remove(DATA + "/" + i + "/arcaea.json")
            nnl = json.loads(read(TOOLS + "/nnl.json"))
            for a in nnl:
                if a == i:
                    nnl.remove(a)
            subscribe = json.loads(read(TOOLS + "/subscribe.json"))
            for a in subscribe:
                if a == i:
                    subscribe.remove(a)
            write(TOOLS + "/nnl.json",nnl)
            write(TOOLS + "/subscribe.json", subscribe)
            os.rmdir(DATA + "/" + i)
        except:
            logger.info("删除文件夹" + i + "失败，未知错误。")
    dlt_count = len(groups)
    await flushdata.finish("好啦，刷新完成！\n删除了" + str(dlt_count) + "个文件夹。")

fix = on_command("fix",priority=5)
@fix.handle()
async def _(event: GroupMessageEvent):
    files = os.listdir(DATA + "/" + str(event.group_id))
    missing = []
    right = ["webhook.json","marry.json","welcome.txt","banword.json","wiki.json","arcaea.json","opening.json","record.json","jx3group.json"]
    fix_data = {"webhook.json":"[]","marry.json":"[]","welcome.txt":"欢迎入群！","banword.json":"[]","wiki.json":"{\"startwiki\":\"\",\"interwiki\":[]}","arcaea.json":"{}","opening.json":"[]","record.json":"[]","jx3group.json":"{\"group\":\"" + str(event.group_id) + "\",\"server\":\"\",\"leader\":\"\",\"leaders\":[],\"name\":\"\",\"status\":false}"}
    for i in right:
        if i not in files:
            missing.append(i)
    for i in missing:
        write(DATA + "/" + str(event.group_id) + "/" + i, fix_data[i])
    await fix.finish("已补全本群数据文件~")