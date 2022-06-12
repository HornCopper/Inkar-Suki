import json,sys,nonebot
from nonebot import get_bot, on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.log import logger
from nonebot.params import CommandArg
TOOLS = nonebot.get_driver().config.tools_path
DATA = TOOLS[:TOOLS.find("/tools")]+"/data"
sys.path.append(str(TOOLS))
from permission import checker, error
from http_ import http
from file import read, write
from config import Config

def already(reponame: str, group) -> bool:
    final_path = DATA + "/" + group + "/" + "webhook.json"
    cache = open(final_path,mode="r")
    repos = json.loads(cache.read())
    for i in repos:
        if i == reponame:
            return True
    return False
repo = on_command("repo", priority=5)
@repo.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    reponame = args.extract_plain_text()
    status_code = await http.get_status("https://github.com/"+reponame)
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
    status_code = await http.get_status("https://github.com/"+repo_name)
    if status_code != 200:
        await repo.finish(f"唔……绑定失败。\n错误码：{status_code}")
    else:
        if already(repo_name, str(event.group_id)) == False:
            cache = open(DATA+"/"+group+"/"+"webhook.json",mode="r")
            new = json.loads(cache.read()).append(repo_name)
            cache.close()
            cache = open(DATA+"/"+group+"/"+"webhook.json",mode="w")
            cache.write(new)
            cache.close()
            webhook.finish("绑定成功！")
        else:
            webhook.finish("唔……绑定失败：已经绑定过了。")
unbind = on_command("unbindrepo",aliases={"unbind_webhook"},priority=5)
@unbind.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
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
    info = json.loads(read(TOOLS+"/webhook.json"))
    if repo == "-a":
        for i in info:
            if i["group"] == group:
                info.remove(i)
                write(TOOLS+"/webhook.json", json.dumps(info))
                await unbind.finish("解绑成功！")
    if group_and_repo_exist(group, repo) == False:
        await unbind.finish("唔……这个群没有绑定这个仓库哦~")
    else:
        for i in info:
            if i["group"] == group:
                for b in i["repo"]:
                    if b == repo:
                        if len(i["repo"]) == 1:
                            info.remove(i)
                            write(TOOLS+"/webhook.json", json.dumps(info))
                            await unbind.finish("已解绑所有此群的Webhook！")
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
    except Exception as e:
        msg = f"Event {event} has not been supported."
        return {"status":"500","message":msg, "error":e}
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
                try:
                    response = await bot.call_api("send_group_msg", group_id=int(group), message=message)
                except:
                    try:
                        response = await bot.call_api("send_group_msg", group_id=int(group), message="唔……刚刚发送消息失败了哦（原因懂的都懂），重新发送：\n"+message)
                        logger.info("Webhook推送失败：被风控，重新发送消息ID为"+response["message_id"])
                    except:
                        logger.info("Webhook推送失败：被风控，重新发送失败。")
                        return
                logger.info("Webhook推送成功：消息ID为"+str(response["message_id"]))
