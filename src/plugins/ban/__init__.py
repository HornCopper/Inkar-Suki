from nonebot import get_bot, on_command
from nonebot.exception import ActionFailed
from src.tools.basic import *
from src.tools.config import Config
from src.tools.utils import checknumber
from src.tools.file import read, write
from src.tools.permission import checker, error

import json

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event, Bot
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, CommandStart


leave_msg = f"{Config.name}要离开这里啦，{Config.name}还没有学会人类的告别语，但是数据库中有一句话似乎很适合现在使用——如果还想来找我的话，我一直在这里（650495414）。"

add_ = """“假如再无法遇见你，祝你早安、午安和晚安。”
——《楚门的世界》"
"""

leave_msg = leave_msg + "\n" + add_

def in_it(qq: str):
    for i in json.loads(read(TOOLS + "/ban.json")):
        if i == qq:
            return True
    return False


ban = on_command("ban", force_whitespace=True, priority=5)  # 封禁，≥10的用户无视封禁。


@ban.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10):
        await ban.finish(error(10))
    sb = args.extract_plain_text()
    self_protection = False
    if sb in Config.owner:
        await ban.send("不能封禁机器人主人，这么玩就不好了，所以我先把你ban了QwQ")
        sb = str(event.user_id)
        self_protection = True
    if not sb:
        await ban.finish("您输入了什么？")
    elif not checknumber(sb):
        await ban.finish("不能全域封禁不是纯数字的QQ哦~")
    elif in_it(sb):
        return ban.finish("唔……全域封禁失败，这个人已经被封禁了。")
    else:
        now = json.loads(read(TOOLS + "/ban.json"))
        now.append(sb)
        write(TOOLS + "/ban.json", json.dumps(now))
        if self_protection:
            return
        await ban.finish(f"好的，已经全域封禁({sb})。")

unban = on_command("unban", force_whitespace=True, priority=5)  # 解封


@unban.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10):
        await ban.finish(error(10))
    sb = args.extract_plain_text()
    if checknumber(sb) is False:
        await ban.finish("不能全域封禁不是纯数字的QQ哦~")
    if sb is False:
        await unban.finish("您输入了什么？")
    if in_it(sb) is False:
        await unban.finish("全域解封失败，并没有封禁此人哦~")
    now = json.loads(read(TOOLS + "/ban.json"))
    for i in now:
        if i == sb:
            now.remove(i)
    write(TOOLS + "/ban.json", json.dumps(now))
    await ban.finish(f"好的，已经全域解封({sb})。")


@preprocess.handle()
async def _(matcher: Matcher, event: Event):
    info = json.loads(read(TOOLS + "/ban.json"))
    if str(event.user_id) in info and not checker(str(event.user_id),10):
        matcher.stop_propagation()
    else:
        pass


dismiss = on_command("dismiss", aliases={"移除音卡"}, force_whitespace=True, priority=5)


@dismiss.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    user_permission = personal_data["role"] in ["owner", "admin"]
    if not (checker(str(event.user_id), 10) or user_permission):
        await dismiss.finish(f"唔……只有群主或管理员才能移除{Config.name}哦~")
    else:
        await dismiss.send(f"确定要让{Config.name}离开吗？如果是，请再发送一次“移除音卡”。")


@dismiss.got("confirm")
async def _(bot: Bot, event: Event, confirm: Message = Arg()):
    u_input = confirm.extract_plain_text()
    if u_input == "移除音卡":
        await dismiss.send(leave_msg)
        for i in Config.notice_to[str(event.self_id)]:
            await bot.call_api("send_group_msg", group_id=int(i), message=f"{Config.name}按他们的要求，离开了{event.group_id}。")
        await bot.call_api("set_group_leave", group_id=event.group_id)


recovery = on_command("recovery", aliases={"重置音卡"}, force_whitespace=True, priority=5)

@recovery.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    user_permission = personal_data["role"] in ["owner", "admin"]
    if not (checker(str(event.user_id), 10) or user_permission):
        await recovery.finish(f"唔……只有群主或管理员才能重置{Config.name}哦~")
    else:
        await recovery.send(f"确定要重置{Config.name}数据吗？如果是，请再发送一次“重置音卡”。\n注意：所有本群数据将会清空，包括绑定和订阅，该操作不可逆！")

import shutil

@recovery.got("confirm")
async def _(bot: Bot, event: Event, confirm: Message = Arg()):
    u_input = confirm.extract_plain_text()
    if u_input == "重置音卡":
        if os.path.exists(DATA + "/" + str(event.group_id)):
            shutil.rmtree(DATA + "/" + str(event.group_id))
        group_id = str(event.group_id)
        files = {
            "blacklist.json": [],
            "settings.json": {"server": "", "group": group_id, "subscribe": [], "addtions": [], "welcome": "欢迎入群！"},
            "webhook.json": [],
            "opening.json": [],
            "wiki.json": {"startwiki":"","interwiki":[]},
            "record.json": []
        }
        status = []
        for i in list(files):
            if os.path.exists(DATA + "/" + group_id + "/" + i):
                status.append(True)
                continue
            status.append(False)
            write(DATA + "/" + group_id + "/" + i, json.dumps(files[i]))
        await dismiss.send("重置成功！可以重新开始绑定本群数据了！")