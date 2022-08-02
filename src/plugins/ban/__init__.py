import json
import sys
import nonebot
from nonebot import on_command, on_message
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event, Bot, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
TOOLS = nonebot.get_driver().config.tools_path
DATA = TOOLS[:-5] + "data"
sys.path.append(str(TOOLS))
from permission import checker, error
from file import read, write
from utils import checknumber

ban = on_command("ban", aliases={"block"}, priority=5)
def in_it(qq: str):
    for i in json.loads(read(TOOLS+"/ban.json")):
        if i == qq:
            return True
    return False
@ban.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),10) == False:
        await ban.finish(error(10))
    sb = args.extract_plain_text()
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
        await ban.finish(f"好的，已经全域封禁{sb_name}({sb})。")
unban = on_command("unban",aliases={"unblock"},priority=5)
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
banned = on_message(priority=2,block=False)
@banned.handle()
async def _(matcher: Matcher, event: Event):
    info = json.loads(read(TOOLS+"/ban.json"))
    if str(event.user_id) in info and checker(str(event.user_id),10) == False:
        matcher.stop_propagation()
    else:
        pass

def check_group_banned(obj,group):
    bans = json.loads(read(DATA+"/"+group+"/block.json"))
    for i in bans:
        if i == obj:
            return True
    return False

group_ban = on_command("group_ban",priority=5)
@group_ban.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if checker(str(event.user_id),9) == False:
        await ban.finish(error(9))
    sb = args.extract_plain_text()
    if checknumber(sb) == False:
        await ban.finish("不能全域封禁不是纯数字的QQ哦~")
    info = await bot.call_api("get_stranger_info",user_id=int(sb))
    sb_name = info["nickname"]
    now = json.loads(read(DATA+"/"+str(event.group_id)+"/block.json"))
    if check_group_banned(sb,str(event.group_id)) == False:
        now.append(sb)
        write(DATA+"/"+str(event.group_id)+"/block.json",json.dumps(now))
    else:
        await group_ban.finish("封禁失败，本群已经封禁过了哦~")
    try:
        bot.call_api("set_group_kick",group_id=event.group_id,user_id=int(sb))
    except:
        pass
    await group_ban.finish("喵~成功在本群封禁"+sb_name+f"({sb})。")

group_unban = on_command("group_unban",priority=5)
@group_unban.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if checker(str(event.user_id),9) == False:
        await ban.finish(error(9))
    sb = args.extract_plain_text()
    if checknumber(sb) == False:
        await ban.finish("不能全域解封不是纯数字的QQ哦~")
    now = json.loads(read(DATA+"/"+str(event.group_id)+"/block.json"))
    if check_group_banned(sb,str(event.group_id)) == False:
        await group_unban.finish("解除本群封禁失败，尚未封禁此人。")
    else:
        now.remove(sb)
        write(DATA+"/"+str(event.group_id)+"/block.json",json.dumps(now))
        await group_unban.finish("解除其在本群的封禁成功！")
        
group_banned = on_message(block=False,priority=3)
@group_banned.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    if checker(str(event.user_id),5):
        return
    sb = str(event.user_id)
    group = str(event.group_id)
    if check_group_banned(sb,group):
        await bot.call_api("set_group_kick",group_id=event.group_id,user_id=event.user_id)
        await bot.call_api("send_group_msg",group_id=event.group_id,message="喵~已为本群拦截不速之客：\n"+sb)
        matcher.stop_propagation()
    else:
        return