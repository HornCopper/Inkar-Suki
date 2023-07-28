from src.tools.config import Config
from src.tools.file import read, write
from src.tools.permission import checker, error
import nonebot
import json

from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot import on_notice, on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, NoticeEvent
from nonebot.params import CommandArg

TOOLS = nonebot.get_driver().config.tools_path
DATA = TOOLS[:-5] + "data"


def checknumber(number):  # 检查参数是否为`int`。
    number.isdecimal()


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
    """
    入群自动发送帮助信息。
    """
    if event.notice_type == "group_increase":
        obj = event.user_id
        group = event.group_id
        bots = Config.bot
        if str(obj) == bots[0]:
            msg = "欢迎使用Inkar Suki！如需帮助请发送+help或查询文档哦~\nhttps://inkar-suki.codethink.cn\n若为初次使用，请申请人在本群发送+reg进行注册方可使用哦~"
        else:
            msg = ms.at(obj) + read(DATA + "/" + str(group) + "/welcome.txt")
        await bot.call_api("send_group_msg", group_id=group, message=msg)
    elif event.notice_type == "group_decrease":
        if event.sub_type == "kick_me":
            kicker = str(event.operator_id)
            if banned(kicker) == False:
                banlist = json.loads(read(TOOLS + "/ban.json"))
                banlist.append(kicker)
                write(TOOLS + "/ban.json", json.dumps(banlist))
                return
            else:
                return

welcome_msg_edit = on_command("welcome", priority=5)


@welcome_msg_edit.handle()
async def __(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    欢迎语的修改。
    """
    if checker(str(event.user_id), 5) == False:
        await welcome_msg_edit.finish(error(5))
    msg = args.extract_plain_text()
    if msg:
        write(DATA + "/" + str(event.group_id) + "/welcome.txt", msg)
        await welcome_msg_edit.finish("喵~已设置入群欢迎！")
    else:
        await welcome_msg_edit.finish("您输入了什么？")
