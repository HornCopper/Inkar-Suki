from nonebot import on_command, on_message
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event, Bot
from nonebot.params import CommandArg
import json
import sys
sys.path.append("/root/nb/src/tools")
from permission import checker, error
from file import read, write
def checknumber(number):
    return number.isdecimal()
ban = on_command("ban",aliases={"block"},priority=5)

def in_it(qq: str):
    for i in json.loads(read("/root/nb/src/tools/ban.json")):
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
        await ban.finish("不能封禁不是纯数字的QQ哦~")
    info = await bot.call_api("get_stranger_info",user_id=int(sb))
    if info["user_id"] == 0:
        await ban.finish("唔……封禁失败，没有这个人哦~")
    elif in_it(sb):
        return ban.finish("唔……封禁失败，这个人已经被封禁了。")
    else:
        now = json.loads(read("/root/nb/src/tools/ban.json"))
        now.append(sb)
        write("/root/nb/src/tools/ban.json",json.dumps(now))
        sb_name = info["nickname"]
        await ban.finish(f"好的，已经封禁{sb_name}({sb})。")

unban = on_command("unban",aliases={"unblock"},priority=5)

@unban.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),10) == False:
        await ban.finish(error(10))
    sb = args.extract_plain_text()
    info = await bot.call_api("get_stranger_info",user_id=int(sb))
    sb_name = info["nickname"]
    if sb == False:
        await unban.finish("您输入了什么？")
    if in_it(sb) == False:
        await unban.finish("解封失败，并没有封禁此人哦~")
    now = json.loads(read("/root/nb/src/tools/ban.json"))
    for i in now:
        if i == sb:
            now.remove(i)
    write("/root/nb/src/tools/ban.json",json.dumps(now))
    await ban.finish(f"好的，已经解封{sb_name}({sb})。")

ban = on_message(priority=1,block=False)

@ban.handle()
async def _(matcher: Matcher, event: Event):
    info = json.loads(read("/root/nb/src/tools/webhook.json"))
    if str(event.user_id) in info:
        matcher.stop_propagation()
    else:
        pass
