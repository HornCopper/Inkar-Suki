import json
import sys
import nonebot

from nonebot import on_command, on_message
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event, Bot, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
DATA = TOOLS[:-7] + "data"

from permission import checker, error
from file import read, write
from utils import checknumber
from config import Config

def in_it(qq: str):
    for i in json.loads(read(TOOLS+"/ban.json")):
        if i == qq:
            return True
    return False

ban = on_command("ban",priority=5)
@ban.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    sb = args.extract_plain_text()
    self_protection = False
    if sb in Config.owner:
        await ban.send("不能封禁机器人主人，这么玩就不好了，所以我先把你ban了QwQ")
        sb = str(event.user_id)
        self_protection = True
    if checker(str(event.user_id),10) == False:
        if self_protection == False:
            await ban.finish(error(10))
    if sb == False:
        await ban.finish("您输入了什么？")
    if checknumber(sb) == False:
        await ban.finish("不能全域封禁不是纯数字的QQ哦~")
    info = await bot.call_api("get_stranger_info",user_id=int(sb))
    if info["user_id"] == 0:
        await ban.finish("唔……全域封禁失败，没有这个人哦~")
    elif in_it(sb):
        return ban.finish("唔……全域封禁失败，这个人已经被封禁了。")
    else:
        now = json.loads(read(TOOLS+"/ban.json"))
        now.append(sb)
        write(TOOLS+"/ban.json", json.dumps(now))
        sb_name = info["nickname"]
        if self_protection:
            return
        await ban.finish(f"好的，已经全域封禁{sb_name}({sb})。")

unban = on_command("unban" ,priority=5)
@unban.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),10) == False:
        await ban.finish(error(10))
    sb = args.extract_plain_text()
    if checknumber(sb) == False:
        await ban.finish("不能全域封禁不是纯数字的QQ哦~")
    info = await bot.call_api("get_stranger_info",user_id=int(sb))
    sb_name = info["nickname"]
    if sb == False:
        await unban.finish("您输入了什么？")
    if in_it(sb) == False:
        await unban.finish("全域解封失败，并没有封禁此人哦~")
    now = json.loads(read(TOOLS+"/ban.json"))
    for i in now:
        if i == sb:
            now.remove(i)
    write(TOOLS+"/ban.json", json.dumps(now))
    await ban.finish(f"好的，已经全域解封{sb_name}({sb})。")

banned = on_message(priority=2, block=False)
@banned.handle()
async def _(matcher: Matcher, event: Event):
    info = json.loads(read(TOOLS+"/ban.json"))
    if str(event.user_id) in info and checker(str(event.user_id),10) == False:
        matcher.stop_propagation()
    else:
        pass