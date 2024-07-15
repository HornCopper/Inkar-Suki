from src.tools.basic import *
from src.tools.config import Config
from src.tools.file import read
from src.tools.utils import get_status
from src.tools.permission import checker, error

import json
import nonebot
import os

from fastapi import Request, FastAPI
from nonebot import get_bot, on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.log import logger
from nonebot.params import CommandArg

from .parse import GithubBaseParser


def already(reponame: str, group) -> bool:
    final_path = DATA + "/" + group + "/" + "webhook.json"
    repos = json.loads(read(final_path))
    for i in repos:
        if i == reponame:
            return True
    return False


repo = on_command("repo", force_whitespace=True, priority=5)


@repo.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取`GitHub`仓库的简介图片。
    """
    if args.extract_plain_text() == "":
        return
    reponame = args.extract_plain_text()
    status_code = await get_status("https://github.com/" + reponame)
    if status_code != 200:
        await repo.finish(f"仓库获取失败，请检查后重试哦~\n错误码：{status_code}")
    else:
        img = ms.image(
            "https://opengraph.githubassets.com/c9f4179f4d560950b2355c82aa2b7750bffd945744f9b8ea3f93cc24779745a0/"+reponame)
        await repo.finish(img)

webhook = on_command("bindrepo", aliases={"webhook"}, force_whitespace=True, priority=5)


@webhook.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    添加群聊响应的`Webhook`仓库。
    """
    if args.extract_plain_text() == "":
        return
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if not group_admin:
        if not checker(str(event.user_id), 5):
            await webhook.finish(error(5))
    repo_name = args.extract_plain_text()
    status_code = await get_status("https://github.com/" + repo_name)
    if status_code != 200:
        await repo.finish(f"唔……绑定失败。\n错误码：{status_code}")
    else:
        group = str(event.group_id)
        if already(repo_name, group) is False:
            cache = open(DATA + "/" + group + "/" + "webhook.json", mode="r")
            now = json.loads(cache.read())
            now.append(repo_name)
            cache.close()
            cache = open(DATA + "/" + group + "/" + "webhook.json", mode="w")
            cache.write(json.dumps(now))
            cache.close()
            await webhook.finish("绑定成功！")
        else:
            await webhook.finish("唔……绑定失败：已经绑定过了。")

unbind = on_command("unbindrepo", aliases={"unbind_webhook"}, force_whitespace=True, priority=5)


@unbind.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    与上一个函数功能相反。
    """
    if args.extract_plain_text() == "":
        return
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if not group_admin:
        if not checker(str(event.user_id), 9):
            await unbind.finish(error(9))
    repo = args.extract_plain_text()
    group = str(event.group_id)
    if already(repo, group) is False:
        await unbind.finish("唔……解绑失败：尚未绑定此仓库。")
    else:
        cache = open(DATA + "/" + group + "/webhook.json", mode="r")
        now = json.loads(cache.read())
        now.remove(repo)
        cache.close()
        cache = open(DATA + "/" + group + "/webhook.json", mode="w")
        cache.write(json.dumps(now))
        cache.close()
        await unbind.finish("解绑成功！")

app: FastAPI = nonebot.get_app()


@app.post(Config.web_path)
async def recWebHook(req: Request):
    """
    接受`Webhook`的`POST`接口，路径来源于`config.py`。
    """
    body = await req.json()
    repo = body["repository"]["full_name"]
    event = req.headers.get("X-GitHub-Event")
    current_handler = GithubBaseParser
    try:
        message = "[GitHub] " + getattr(current_handler, event)(body)
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
