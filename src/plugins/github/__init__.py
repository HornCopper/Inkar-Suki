import json,sys,nonebot
from nonebot import get_bot, on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.log import logger
from nonebot.params import CommandArg
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
from permission import checker, error
from http_ import http
from file import read, write
from config import Config

def checknumber(number):
    return number.isdecimal()
def group_exist(group):
    info = json.loads(read(TOOLS+"/webhook.json"))
    for i in info:
        if i["group"] == group:
            return True
    return False
def group_and_repo_exist(group, repo):
    info = json.loads(read(TOOLS+"/webhook.json"))
    for i in info:
        if i["group"] == group:
            for q in i["repo"]:
                if q == repo:
                    return True
    return False
repo = on_command("repo", priority=5)
@repo.handle()
async def _(event: Event, args: Message = CommandArg()):
    reponame = args.extract_plain_text()
    status_code = await http.get_status("https://github.com/"+reponame)
    if status_code != 200 and status_code != 301 and status_code != 302:
        await repo.finish(f"仓库获取失败，请检查后重试哦~\n错误码：{status_code}")
    else:
        img = ms.image("https://opengraph.githubassets.com/c9f4179f4d560950b2355c82aa2b7750bffd945744f9b8ea3f93cc24779745a0/"+reponame)
        await repo.finish(img)
webhook = on_command("bindrepo",aliases={"webhook"},priority=5)
@webhook.handle()
async def _(event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),9) == False:
        await webhook.finish(error(9))
    cmd = args.extract_plain_text()
    args = cmd.split(" ")
    if len(args)>2:
        await wa.finish("唔……你的参数有多余的哦~")
    if len(args)<2:
        await wa.finish("唔……你好像缺了一些参数哦~")
    group = args[0]
    repo = args[1]
    if repo.find("/") == -1:
        await webhook.finish("这不是有效的Repo名，正确的格式应为{作者/组织}/{项目名称}")
    if checknumber(group) == False:
        await webhook.finish("这不是有效的QQ群号！")
    repo_status = await http.get_status("https://github.com/"+repo)
    if repo_status != 200:
        await webhook.finish("Repo不存在哦~")
    if group_and_repo_exist(group, repo):
        await webhook.finish("Repo已经添加过了哦~")
    if group_exist(group):
        info = json.loads(read(TOOLS+"/webhook.json"))
        for i in info:
            if i["group"] == group:
                i["repo"].append(repo)
        write(TOOLS+"/webhook.json", json.dumps(info))
        await webhook.finish("绑定成功！")
    else:
        new = {"group": group, "repo": [repo]}
        info = json.loads(read(TOOLS+"/webhook.json"))
        info.append(new)
        write(TOOLS+"/webhook.json", json.dumps(info))
        await webhook.finish("绑定成功！")
unbind = on_command("unbindrepo",aliases={"unbind_webhook"},priority=5)
@unbind.handle()
async def _(event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),9) == False:
        await unbind.finish(error(9))
    cmd = args.extract_plain_text()
    args = cmd.split(" ")
    if len(args)>2:
        await unbind.finish("唔……你的参数有多余的哦~")
    if len(args)<2:
        await unbind.finish("唔……你好像缺了一些参数哦~")
    group = args[0]
    repo = args[1]
    if repo.find("/") == -1 and repo != "-a":
        await unbind.finish("这不是有效的Repo名，正确的格式应为{作者/组织}/{项目名称}")
    if checknumber(group) == False:
        await unbind.finish("这不是有效的QQ群号啦！")
    if group_exist(group) == False:
        await unbind.finish("唔……这个群尚未绑定任何Repo~")
    if group_and_repo_exist(group, repo) == False:
        await unbind.finish("唔……这个群没有绑定这个仓库哦~")
    info = json.loads(read(TOOLS+"/webhook.json"))
    if repo == "-a":
        for i in info:
            if i["group"] == group:
                info.remove(i)
                write(TOOLS+"/webhook.json", json.dumps(info))
                await unbind.finish("解绑成功！")
    else:
        for i in info:
            if i["group"] == group:
                for b in i["repo"]:
                    if b == repo:
                        if len(i["repo"]) == 1:
                            info.remove(i)
                            write(TOOLS+"/webhook.json", json.dumps(info))
                            await unbind.finish("解绑成功！")
                        else:
                            i["repo"].remove(b)
                            write(TOOLS+"/webhook.json", json.dumps(info))
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
    except:
        msg = f"Event {event} has not been supported."
        return {"status":"500","message":msg}
    bots: list = Config.bot
    for i in bots:
        bot = get_bot(i)
        await sendNbMessage(bot, message, repo)
    return {"status":200}

async def sendNbMessage(bot: Bot, message, repo):
    group_id_list = json.loads(read(TOOLS+"/webhook.json"))
    for i in group_id_list:
        for m in i["repo"]:
            if m == repo:
                group = i["group"]
                response = await bot.call_api("send_group_msg", group_id=int(group), message=message)
                logger.info(response)
