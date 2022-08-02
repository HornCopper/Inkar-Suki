import json
import sys
import nonebot
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot import on_command
from nonebot import on_message
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.params import CommandArg
TOOLS = nonebot.get_driver().config.tools_path
DATA = TOOLS[:-5] + "data"
sys.path.append(str(TOOLS))
from permission import checker, error
from file import read, write
global flag
banword = on_command("banword", priority=5)
@banword.handle()
async def __(event: GroupMessageEvent, args: Message = CommandArg()):
    bw = args.extract_plain_text()
    if checker(str(event.user_id), 5) == False:
        await banword.finish(error(5))
    if bw:
        now = json.loads(read(DATA+"/"+str(event.group_id)+"/banword.json"))
        if bw in now:
            await banword.finish("唔……封禁失败，已经封禁过了。")
        now.append(bw)
        write(DATA+"/"+str(event.group_id)+"/banword.json", json.dumps(now, ensure_ascii=False))
        await banword.finish("已成功封禁词语！")
    else:
        await banword.finish("您封禁了什么？")
unbanword = on_command("unbanword",priority=5)
@unbanword.handle()
async def ___(event: GroupMessageEvent, args: Message = CommandArg()):
    if checker(str(event.user_id),5) == False:
        await unbanword.finish(error(5))
    cmd = args.extract_plain_text()
    if cmd:
        now = json.loads(read(DATA+"/"+str(event.group_id)+"/banword.json"))
        try:
            now.remove(cmd)
            write(DATA+"/"+str(event.group_id)+"/banword.json", json.dumps(now, ensure_ascii=False))
            await unbanword.finish("成功解封词语！")
        except ValueError:
            await unbanword.finish("您解封了什么？")
    else:
        await unbanword.finish("您解封了什么？")
banned_word = on_message(priority=3, block=False)
@banned_word.handle()
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent):
    if checker(str(event.user_id),5):
        return
    flag = False
    banwordlist = json.loads(read(DATA+"/"+str(event.group_id)+"/banword.json"))
    msg = event.get_plaintext()
    id_ = str(event.message_id)
    for i in banwordlist:
        if msg.find(i) != -1:
            flag = True
    if flag:
        sb = event.user_id
        try:
            group = event.group_id
            await bot.call_api("delete_msg",message_id=id_)
            await bot.call_api("set_group_ban", group_id = group, user_id = sb, duration = 60)
            msg = ms.at(sb) + "唔……你触发了违禁词，已经给你喝了1分钟的红茶哦~"
            matcher.stop_propagation()
            await banned_word.finish(msg)
        except:
            pass
    else:
        pass