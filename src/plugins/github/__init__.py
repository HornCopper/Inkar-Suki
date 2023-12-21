from src.tools.dep import *
from .parse import main
from src.tools.config import Config
from src.tools.file import read
from src.tools.utils import get_status
from src.tools.permission import checker, error
import json
import sys
import nonebot
import os

from fastapi import Request, FastAPI
from nonebot import get_bot, on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.log import logger
from nonebot.params import CommandArg


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
    """
    获取`GitHub`仓库的简介图片。
    """
    reponame = args.extract_plain_text()
    status_code = await get_status("https://github.com/" + reponame)
    if status_code != 200:
        return await repo.finish(f"仓库获取失败，请检查后重试哦~\n错误码：{status_code}")
    else:
        img = ms.image(
            "https://opengraph.githubassets.com/c9f4179f4d560950b2355c82aa2b7750bffd945744f9b8ea3f93cc24779745a0/"+reponame)
        return await repo.finish(img)

webhook = on_command("bindrepo", aliases={"webhook"}, priority=5)


@webhook.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    添加群聊响应的`Webhook`仓库。
    """
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if not group_admin:
        x = Permission(event.user_id).judge(5, '添加群聊响应的wenhook')
        if not x.success:
            return await webhook.finish(x.description)
    repo_name = args.extract_plain_text()
    status_code = await get_status("https://github.com/" + repo_name)
    if status_code != 200:
        return await repo.finish(f"唔……绑定失败。\n错误码：{status_code}")
    else:
        group = str(event.group_id)
        if already(repo_name, group) == False:
            cache = open(DATA + "/" + group + "/" + "webhook.json", mode="r")
            now = json.loads(cache.read())
            now.append(repo_name)
            cache.close()
            cache = open(DATA + "/" + group + "/" + "webhook.json", mode="w")
            cache.write(json.dumps(now))
            cache.close()
            return await webhook.finish("绑定成功！")
        else:
            return await webhook.finish("唔……绑定失败：已经绑定过了。")

unbind = on_command("unbindrepo", aliases={"unbind_webhook"}, priority=5)


@unbind.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    与上一个函数功能相反。
    """
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if not group_admin:
        
        x = Permission(event.user_id).judge(9, '解封用户')
        if not x.success:
            return await unbind.finish(x.description)
    repo = args.extract_plain_text()
    group = str(event.group_id)
    if already(repo, group) == False:
        return await unbind.finish("唔……解绑失败：尚未绑定此仓库。")
    else:
        cache = open(DATA + "/" + group + "/webhook.json", mode="r")
        now = json.loads(cache.read())
        now.remove(repo)
        cache.close()
        cache = open(DATA + "/" + group + "/webhook.json", mode="w")
        cache.write(json.dumps(now))
        cache.close()
        return await unbind.finish("解绑成功！")

app: FastAPI = nonebot.get_app()


@app.post(Config.web_path)
async def recWebHook(req: Request):
    """
    接受`Webhook`的`POST`接口，路径来源于`config.py`。
    """
    body = await req.json()
    repo = body["repository"]["full_name"]
    event = req.headers.get("X-GitHub-Event")
    try:
        message = "[GitHub] " + getattr(main, event)(body)
        message = message.replace("codethink-cn", "CodeThink-CN")
    except Exception as e:
        msg = f"Event {event} has not been supported."
        return {"status": "500", "message": msg, "error": e}
    bots: list = Config.bot
    for i in bots:
        bot = get_bot(i)
        await sendm(bot, message, repo)
    return {"status": 200}


async def sendm(bot, message, repo):
    """
    推送`Webhook`。
    """
    groups = os.listdir(DATA)
    send_group = []
    for i in groups:
        if repo in json.loads(read(DATA + "/" + i + "/webhook.json")):
            send_group.append(int(i))
    for i in send_group:
        response = await bot.call_api("send_group_msg", group_id=int(i), message=message)
        logger.info("Webhook推送成功：消息ID为" + str(response["message_id"]))
