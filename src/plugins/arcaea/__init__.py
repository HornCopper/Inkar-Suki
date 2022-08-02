import sys
import nonebot
import json
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import CommandArg
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
DATA = TOOLS[:-5] + "data"
from .arcaea import getUserInfo, judgeWhetherPlayer
from utils import checknumber
from file import read, write

arcaea_userinfo = on_command("arcuser",priority=5)
@arcaea_userinfo.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text()
    if arg == False:
        await arcaea_userinfo.finish("尚未输入任何信息，没办法帮你找哦~")
    if checknumber(arg):
        msg = await getUserInfo(usercode=int(arg))
    else:
        msg = await getUserInfo(nickname=arg)
    await arcaea_userinfo.finish(msg)

arcaea_binduser = on_command("arcbind",priority=5)
@arcaea_binduser.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text()
    if arg == False:
        await arcaea_binduser.finish("尚未输入任何信息，没办法帮你找哦~")
    present_data = json.loads(read(DATA+"/"+str(event.group_id)+"/arcaea.json"))
    if checknumber(arg):
        resp = await judgeWhetherPlayer(usercode=int(arg))
        present_data[str(event.user_id)] = resp[1]
    else:
        resp = await judgeWhetherPlayer(nickname=arg)
        present_data[str(event.user_id)] = resp[1]
    if resp:
        write(DATA+"/"+str(event.group_id)+"/arcaea.json", json.dumps(present_data))
        await arcaea_binduser.finish("绑定成功："+ resp[0]) 
    else:
        await arcaea_binduser.finish("您输入的好友码/用户名查不到哦，请检查后重试~")
        
arcaea_unbind = on_command("arcunbind",priority=5)
@arcaea_unbind.handle()
async def _(event: GroupMessageEvent):
    present_data = json.loads(read(DATA+"/"+str(event.group_id)+"/arcaea.json"))
    if present_data[str(event.user_id)]:
        present_data.pop(str(event.user_id))
        write(DATA+"/"+str(event.group_id)+"/arcaea.json", json.dumps(present_data))
        await arcaea_unbind.finish("已解绑Arcaea账号~以后使用相关命令均需重新绑定哦~") 
    else:
        await arcaea_unbind.finish("唔……尚未绑定过Arcaea，无法解绑啦！")