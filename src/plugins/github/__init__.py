import json
import sys
import nonebot
import os
from nonebot import get_bot, on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.log import logger
from nonebot.params import CommandArg
TOOLS = nonebot.get_driver().config.tools_path
DATA = TOOLS[:-5] + "data"
sys.path.append(str(TOOLS))
from permission import checker, error
from utils import get_status
from file import read, write
from config import Config

def already(reponame: str, group) -> bool:
    final_path = DATA + "/" + group + "/" + "webhook.json"
    repos = json.loads(read(final_path))
    for i in repos:
        if i == reponame:
            return True
    return False
repo = on_command("repo", priority=5)
@repo.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    reponame = args.extract_plain_text()
    status_code = await get_status("https://github.com/"+reponame)
    if status_code != 200:
        await repo.finish(f"仓库获取失败，请检查后重试哦~\n错误码：{status_code}")
    else:
        img = ms.image("https://opengraph.githubassets.com/c9f4179f4d560950b2355c82aa2b7750bffd945744f9b8ea3f93cc24779745a0/"+reponame)
        await repo.finish(img)
webhook = on_command("bindrepo",aliases={"webhook"},priority=5)
@webhook.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if checker(str(event.user_id),9) == False:
        await unbind.finish(error(9))
    repo_name = args.extract_plain_text()
    status_code = await get_status("https://github.com/"+repo_name)
    if status_code != 200:
        await repo.finish(f"唔……绑定失败。\n错误码：{status_code}")
    else:
        group=str(event.group_id)
        if already(repo_name, group) == False:
            cache = open(DATA+"/"+group+"/"+"webhook.json",mode="r")
            now = json.loads(cache.read())
            now.append(repo_name)
            cache.close()
            cache = open(DATA+"/"+group+"/"+"webhook.json",mode="w")
            cache.write(json.dumps(now))
            cache.close()
            await webhook.finish("绑定成功！")
        else:
            await webhook.finish("唔……绑定失败：已经绑定过了。")
unbind = on_command("unbindrepo",aliases={"unbind_webhook"},priority=5)
@unbind.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if checker(str(event.user_id),9) == False:
        await unbind.finish(error(9))
    repo = args.extract_plain_text()
    group = str(event.group_id)
    if already(repo, group) == False:
        await unbind.finish("唔……解绑失败：尚未绑定此仓库。")
    else:
        cache = open(DATA+"/"+group+"/webhook.json",mode="r")
        now = json.loads(cache.read())
        now.remove(repo)
        cache.close()
        cache = open(DATA+"/"+group+"/webhook.json",mode="w")
        cache.write(json.dumps(now))
        cache.close()
        await unbind.finish("解绑成功！")

from fastapi import Request, FastAPI
from .parse import main
app: FastAPI = nonebot.get_app()

@app.post(Config.web_path)
async def recWebHook(req: Request):
    body = await req.json()
    repo = body["repository"]["full_name"]
    event = req.headers.get("X-GitHub-Event")
    try:
        message = "[GitHub] " + getattr(main,event)(body)
        message = message.replace("codethink-cn","CodeThink-CN")
    except Exception as e:
        msg = f"Event {event} has not been supported."
        return {"status":"500","message":msg, "error":e}
    bots: list = Config.bot
    for i in bots:
        bot = get_bot(i)
        await sendm(bot, message, repo)
    return {"status":200}

@app.post("/auth") # 该项用于`assistance`，为方便写代码，放置于此
async def recAuth(req: Request):
    headers = req.headers
    if headers["user"] not in Config.owner:
        return {"status":403}
    else:
        final = []
        groups = os.listdir(DATA)
        for i in groups:
            group_data = json.loads(read(DATA + "/" + i + "/jx3group.json"))
            try:
                if headers["type"] == "all":
                    if group_data["leader"] != "":    
                        name = group_data["name"]
                        owner = group_data["leader"]
                        group = group_data["group"]
                        server = group_data["server"]
                        dict_ = {"name":name,"leader":owner,"group":group,"server":server}
                        final.append(dict_)
                else:
                    if group_data["leader"] != "":
                        if group_data["status"] != False:
                            name = group_data["name"]
                            owner = group_data["leader"]
                            group = group_data["group"]
                            server = group_data["server"]
                            dict_ = {"name":name,"leader":owner,"group":group,"server":server}
                            final.append(dict_)
            except:
                return {"status":502}
        return final

@app.get("/token") # `jx3`提交token的位置。
async def recToken(token: str = None, qq: str = None):
    if token == None:
        return {"status":404,"msg":"没有找到您提交的token哦，请检查您的链接是否有误！如果有不懂的请查询文档或询问作者(QQ:3349104868)！"}
    if qq == None:
        return {"status":404,"msg":"没有找到您提交的QQ号哦，请检查您的链接是否有误！如果有不懂的请查询文档或询问作者(QQ:3349104868)！"}
    else:
        now = json.loads(read(TOOLS + "/token.json"))
        if qq in list(now):
            old_ = now[qq]
            now[qq] = token
            write(TOOLS + "/token.json", json.dumps(now))
            return {"status":200,"msg":"已经更新你的token啦！如果你是不小心更改的，请根据这里附带的旧token，重新拼接url并访问哦~","old_token":old_}
        else:
            now[qq] = token
            write(TOOLS + "/token.json", json.dumps(now))
            return {"status":200,"msg":"已为你存储token，请记住，只有您提交的QQ拥有访问部分功能的权限，他人无法查看哦~"}

async def sendm(bot, message, repo):
    groups = os.listdir("./src/data")
    send_group = []
    for i in groups:
        if repo in json.loads(read(DATA + "/" + i + "/webhook.json")):
            send_group.append(int(i))
    for i in send_group:
        response = await bot.call_api("send_group_msg", group_id=int(i), message=message)
        logger.info("Webhook推送成功：消息ID为"+str(response["message_id"]))