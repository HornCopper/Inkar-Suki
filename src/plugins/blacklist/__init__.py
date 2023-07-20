import json
<<<<<<< HEAD
=======
import sys
>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0
import nonebot

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent
from nonebot.params import CommandArg

TOOLS = nonebot.get_driver().config.tools_path
<<<<<<< HEAD
DATA = TOOLS[:-5] + "data"
=======
sys.path.append(str(TOOLS))
>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0

from src.tools.file import read, write
from src.tools.permission import checker
from src.tools.utils import nodetemp
from src.tools.config import Config

block = on_command("block", aliases={"加黑","避雷"}, priority=5) # 综合避雷名单-添加
@block.handle()
<<<<<<< HEAD
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if (not group_admin) and (checker(str(event.user_id), 5) == False):
        await block.finish("唔……只有管理员和群主有权限避雷哦~")
=======
async def _(event: Event, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    agl_list = json.loads(read(TOOLS + "/agl.json"))
    if (str(event.user_id) not in agl_list) or (checker(str(event.user_id), 10) == False): #achievement group leader
        await block.finish("阁下并未取得成就团团长认证，请联系机器人管理员进行申请。\n编辑黑名单失败。")
>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0
    if len(arg) != 2:
        await block.finish("唔……需要2个参数，第一个参数为玩家名，第二个参数是原因~\n提示：理由中请勿包含空格。")
    sb = arg[0]
    reason = arg[1]
    new = {"ban":sb,"reason":reason}
<<<<<<< HEAD
    group = str(event.group_id)
    now = json.loads(read(DATA + f"/{group}"+ "/blacklist.json"))
=======
    now = json.loads(read(TOOLS + "/blacklist.json"))
>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0
    for i in now:
        if i["ban"] == sb:
            await block.finish("该玩家已加入黑名单。")
    now.append(new)
    write(TOOLS + "/blacklist.json", json.dumps(now, ensure_ascii=False))
    await block.finish("成功将该玩家加入黑名单！")

unblock = on_command("unblock", aliases={"删黑"}, priority=5) # 解除避雷
@unblock.handle()
<<<<<<< HEAD
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if (not group_admin) and (checker(str(event.user_id), 5) == False):
        await unblock.finish("唔……只有管理员和群主有权限避雷哦~")
    if len(arg) != 1:
        await unblock.finish("参数仅为玩家名，请勿附带任何信息！")
    sb = arg[0]
    group = str(event.group_id)
    now = json.loads(read(DATA + f"/{group}"+ "/blacklist.json"))
=======
async def _(event: Event, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    agl_list = json.loads(read(TOOLS + "/agl.json"))
    if (str(event.user_id) not in agl_list) or (checker(str(event.user_id), 10) == False): #achievement group leader
        await unblock.finish("阁下并未取得成就团团长认证，请联系机器人管理员进行申请。\n编辑黑名单失败。")
    if len(arg) != 1:
        await unblock.finish("参数仅为玩家名，请勿附带任何信息！")
    sb = arg[0]
    now = json.loads(read(TOOLS + "/blacklist.json"))
>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0
    for i in now:
        if i["ban"] == sb:
            now.remove(i)
            write(TOOLS + "/blacklist.json", json.dumps(now, ensure_ascii=False))
            await unblock.finish("成功移除该玩家的避雷！")
    await unblock.finish("移除失败！尚未避雷该玩家！")

sblock = on_command("sblock", aliases={"查黑"}, priority=5) # 查询是否在避雷名单
@sblock.handle()
<<<<<<< HEAD
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if (not group_admin) and (checker(str(event.user_id), 5) == False):
        await sblock.finish("唔……只有管理员和群主有权限避雷哦~")
    if len(arg) != 1:
        await sblock.finish("参数仅为玩家名，请勿附带任何信息！")
    sb = arg[0]
    group = str(event.group_id)
    now = json.loads(read(DATA + f"/{group}"+ "/blacklist.json"))
=======
async def _(event: Event, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    agl_list = json.loads(read(TOOLS + "/agl.json"))
    if (str(event.user_id) not in agl_list) or (checker(str(event.user_id), 10) == False): #achievement group leader
        await sblock.finish("阁下并未取得成就团团长认证，请联系机器人管理员进行申请。\n编辑黑名单失败。")
    if len(arg) != 1:
        await sblock.finish("参数仅为玩家名，请勿附带任何信息！")
    sb = arg[0]
    now = json.loads(read(TOOLS + "/blacklist.json"))
>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0
    for i in now:
        if i["ban"] == sb:
            reason = i["reason"]
            msg = f"玩家[{sb}]被避雷的原因为：\n{reason}"
            await sblock.finish(msg)
    await sblock.finish("该玩家尚未被避雷哦~")

lblock = on_command("lblock", aliases={"列黑"}, priority=5) # 列出所有黑名单
@lblock.handle()
async def _(bot: Bot, event: GroupMessageEvent):
<<<<<<< HEAD
    group = str(event.group_id)
    now = json.loads(read(DATA + f"/{group}"+ "/blacklist.json"))
=======
    agl_list = json.loads(read(TOOLS + "/agl.json"))
    if (str(event.user_id) not in agl_list) or (checker(str(event.user_id), 10) == False): #achievement group leader
        await sblock.finish("阁下并未取得成就团团长认证，请联系机器人管理员进行申请。\n操作黑名单失败。")
    now = json.loads(read(TOOLS + "/blacklist.json"))
>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0
    f = ""
    for i in now:
        pl = i["ban"]
        r = i["reason"]
        p = f"玩家名：{pl}\n避雷原因：{r}\n"
        f = f + "\n" + p
    f = f[1:]
    node = nodetemp("避雷查询", Config.bot[0], f)
<<<<<<< HEAD
    await bot.call_api("send_group_forward_msg", group_id = event.group_id, messages = node)
=======
    await bot.call_api("send_group_forward_msg", group_id = event.group_id, messages = node)

from fastapi import FastAPI, Request
app: FastAPI = nonebot.get_app()

# 来点数据接口？

@app.post("/blacklist")
async def _(rec: Request):
    headers = rec.headers
    args = list(headers)
    if "password" not in args or "action" not in args:
        return {"code":422,"reason":"Arguments are missing!"}
    if headers["password"] != read(TOOLS + "/password.txt"):
        return {"code":403,"reason":"Password is incorrect!"}
    if headers["action"] == "add":
        if "sb" not in args or "reason" not in args:
            return {"code":422,"reason":"Arguments are missing!"}
        sb = headers["sb"]
        reason = headers["reason"]
        new = {"ban":sb,"reason":reason}
        now = json.loads(read(TOOLS + "/blacklist.json"))
        for i in now:
            if i["ban"] == sb:
                return {"code":502,"reason":"The player is already banned."}
        now.append(new)
        write(TOOLS + "/blacklist.json", json.dumps(now, ensure_ascii=False))
        return {"code":200,"reason":"Successfully."}
    elif headers["action"] == "del":
        if "sb" not in args:
            return {"code":422,"reason":"Arguments are missing!"}
        sb = headers["sb"]
        now = json.loads(read(TOOLS + "/blacklist.json"))
        for i in now:
            if i["ban"] == sb:
                now.remove(i)
                write(TOOLS + "/blacklist.json", json.dumps(now, ensure_ascii=False))
                return {"code":200,"reason":"Successfully."}
        return {"code":404,"reason":"The player has not been banned yet."}
    elif headers["action"] == "src":
        if "sb" not in args:
            return {"code":422,"reason":"Arguments are missing!"}
        sb = headers["sb"]
        now = json.loads(read(TOOLS + "/blacklist.json"))
        for i in now:
            if i["ban"] == sb:
                reason = i["reason"]
                return {"code":200, "player":sb, "reason":reason}
        return {"code":404, "reason":"The player has not been banned yet."}
    elif headers["action"] == "lst":
        now = json.loads(read(TOOLS + "/blacklist.json"))
        return now
    elif headers["action"] == "vfy":
        if headers["password"] != read(TOOLS + "/password.txt"):
            return {"code":403}
        return {"code":200}
    else:
        return {"code":404,"reason":"No such action!"}
>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0
