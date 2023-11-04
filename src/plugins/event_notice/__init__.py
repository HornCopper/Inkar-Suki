from src.tools.config import Config
from src.tools.file import read, write
from src.tools.permission import checker, error
from src.tools.utils import checknumber

import nonebot
import json
import os

from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot import on_notice, on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, NoticeEvent
from nonebot.params import CommandArg

TOOLS = nonebot.get_driver().config.tools_path
DATA = TOOLS[:-5] + "data"

def banned(sb):  # 检测某个人是否被封禁。
    with open(TOOLS + "/ban.json") as cache:
        banlist = json.loads(cache.read())
        for i in banlist:
            if i == sb:
                return True
        return False

notice = on_notice(priority=5)

@notice.handle()
async def _(bot: Bot, event: NoticeEvent):
    '''
    入群自动发送帮助信息。
    '''
    if event.notice_type == "group_increase":
        obj = event.user_id
        group = event.group_id
        bots = Config.bot
        if str(obj) in bots:
            msg = "欢迎使用Inkar Suki！如需帮助请发送+help或查询文档哦~\nhttps://inkar-suki.codethink.cn\n若为初次使用，请申请人在本群发送+reg进行注册方可使用哦~"
            if event.sub_type == "approve":
                new_path = DATA + "/" + str(event.group_id)
                if os.path.exists(new_path):
                    return
                else:
                    os.mkdir(new_path)
                    write(new_path + "/jx3group.json", "{\"group\":\"" + str(event.group_id) +
                          "\",\"server\":\"\",\"leader\":\"\",\"leaders\":[],\"name\":\"\",\"status\":false}")
                    write(new_path + "/webhook.json", "[]")
                    write(new_path + "/marry.json", "[]")
                    write(new_path + "/welcome.txt", "欢迎入群！")
                    write(new_path + "/banword.json", "[]")
                    write(new_path + "/opening.json", "[]")
                    write(new_path + "/wiki.json", "{\"startwiki\":\"\",\"interwiki\":[]}")
                    write(new_path + "/arcaea.json", "{}")
                    write(new_path + "/record.json", "[]")
                    write(new_path + "/subscribe.json", "[]")
                    write(new_path + "/blacklist.json", "[]")
                    await bot.call_api("send_group_msg", group_id = event.group_id, message ="检测到本群为新群聊，音卡已经自动补全所需要的文件啦！")
        else:
            msg = ms.at(obj) + read(DATA + "/" + str(group) + "/welcome.txt")
        await bot.call_api("send_group_msg", group_id=group, message=msg)
    elif event.notice_type == "group_decrease":
        if event.sub_type == "kick_me":
            for i in Config.notice_to:
                await bot.call_api("send_group_msg", group_id = int(i), message = f"唔……音卡在群聊（{str(event.group_id)}）被移出啦！\n操作者：{str(event.operator_id)}，已自动封禁！")
            kicker = str(event.operator_id)
            if banned(kicker) == False:
                banlist = json.loads(read(TOOLS + "/ban.json"))
                banlist.append(kicker)
                write(TOOLS + "/ban.json", json.dumps(banlist))
                return
            else:
                return
    elif event.notice_type == "group_ban":
        if str(event.user_id) in Config.bot:
            await bot.call_api("set_group_leave", group_id = event.group_id)
            for i in Config.notice_to:
                await bot.call_api("send_group_msg", group_id = int(i), message = f"唔……音卡在群聊（{str(event.group_id)}）检测到被禁言啦，已自动退群！\n操作者：{str(event.operator_id)}，已自动封禁！")
            kicker = str(event.operator_id)
            if banned(kicker) == False:
                banlist = json.loads(read(TOOLS + "/ban.json"))
                banlist.append(kicker)
                write(TOOLS + "/ban.json", json.dumps(banlist))
                return
            else:
                return
    elif event.request_type == "group" and event.sub_type == "invite":
        msg = event.comment
        group = event.group_id
        user = event.user_id
        for i in Config.notice_to:
            await bot.call_api("send_group_msg", group_id = int(i), message = f"收到新的加群申请：\n邀请人：{user}\n群号：{group}\n消息：{msg}")

welcome_msg_edit = on_command("welcome", priority=5)

@welcome_msg_edit.handle()
async def __(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    欢迎语的修改。
    '''
    if checker(str(event.user_id), 5) == False:
        await welcome_msg_edit.finish(error(5))
    msg = args.extract_plain_text()
    if msg:
        write(DATA + "/" + str(event.group_id) + "/welcome.txt", msg)
        await welcome_msg_edit.finish("喵~已设置入群欢迎！")
    else:
        await welcome_msg_edit.finish("您输入了什么？")