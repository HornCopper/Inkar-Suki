import nonebot
import sys
import json

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Event, GroupMessageEvent

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from file import read, write
from utils import data_post

storage = on_command("jx3_storage", aliases={"推栏"}, priority=5)
@storage.handle()
async def _(event: Event, args: Message = CommandArg()):
    data = args.extract_plain_text()
    data = data.split(" ")
    if len(data) != 4:
        await storage.finish("数据录入失败：格式有误。")
    gid = data[0]
    ts = data[1]
    sign = data[2]
    token = data[3]
    qq = str(event.user_id)
    new = {qq:{"globalRoleId":gid,"ts":ts,"sign":sign,"token":token}}
    now = json.loads(read(TOOLS + "/token.json"))
    updated = False
    if qq in list(now):
        now[qq] = {"globalRoleId":gid,"ts":ts,"sign":sign,"token":token}
        updated = True
    else:
        now.append(new)
    write(TOOLS + "/token.json",json.dumps(now))
    if updated:
        await storage.finish("已更新您的数据，该信息仅保存在机器人服务器，不与任何第三方共享。")
    else:
        await storage.finish("已录入您的数据，该信息仅保存在机器人服务器，不与任何第三方共享。")

def getData(qq):
    data = json.loads(read(TOOLS + "/token.json"))
    for i in data:
        if list(i)[0] == qq:
            return i[qq]
    return False

cd = on_command("jx3_cd", aliases={"副本cd"}, priority=5)
@cd.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    data = getData(str(event.user_id))
    if data == False:
        await cd.finish("查询失败，您尚未录入数据。")
    msg = args.extract_plain_text()
    globalRoleId = data["globalRoleId"]
    ts = data["ts"]
    sign = data["sign"]
    token = data["token"]
    remote_data = await data_post(url = "https://w.pvp.xoyo.com/api/h5/parser/cd-process/get-by-role", headers = {"token":token}, json = {"globalRoleId":globalRoleId, "ts":ts, "sign":sign})
    if msg == "":
        final_msg = ""
        for i in remote_data["data"]:
            part = i["mapType"] + i["mapName"] + "\n"
            progress = []
            for x in i["bossProgress"]:
                if x["finished"] == True:
                    progress.append("○")
                else:
                    progress.append("●")
            progress_msg = "".join(progress)
            part = part + f"进度：{progress_msg}"
            final_msg = final_msg + part + "\n"
        final_msg = final_msg[:-1]
        await cd.finish(final_msg)
    else:
        msg = msg.split()
        if len(msg) == 1:
            for i in remote_data["data"]:
                if msg[0] == i["mapType"] + i["mapName"]:
                    part = i["mapType"] + i["mapName"] + "\n"
                    progress = []
                    for x in i["bossProgress"]:
                        if x["finished"] == True:
                            progress.append("○")
                        else:
                            progress.append("●")
                    progress_msg = "".join(progress)
                    part = part + f"进度：{progress_msg}"
                    final_msg = final_msg + part + "\n"
                    final_msg = final_msg[:-1]
            await cd.finish(final_msg)
        elif len(msg) == 2:
            for i in remote_data["data"]:
                if msg[0] == i["mapType"] + i["mapName"]:
                    passed = False
                    found = False
                    for x in i["bossProgress"]:
                        if x["name"] == msg[1] and x["finished"] == True:
                            passed = True
                            found = True
                    progress_msg = "".join(progress)
                    if found == False:
                        final_msg = "未找到该首领，请检查副本名称是否输入正确。"
                    else:
                        if passed:
                            final_msg = "该首领已通关~"
                        else:
                            final_msg = "唔，还没有通过这个首领哦~"
            await cd.finish(final_msg)
        else:
            await cd.finish("参数数量不正确哦，请检查后重试~")