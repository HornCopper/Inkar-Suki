from typing import Union, Any, List, Dict

from nonebot import on_command
from nonebot.adapters import Message, Bot
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
from nonebot.params import CommandArg, Arg

from src.tools.config import Config
from src.tools.utils.num import check_number
from src.tools.permission import checker, error
from src.tools.database import group_db, BannedList, GroupSettings
from src.tools.basic.process import preprocess

leave_msg = f"{Config.bot_basic.bot_name}要离开这里啦，{Config.bot_basic.bot_name}还没有学会人类的告别语，但是数据库中有一句话似乎很适合现在使用——如果还想来找我的话，我一直在这里（650495414）。"

add_ = """“假如再无法遇见你，祝你早安、午安和晚安。”
——《楚门的世界》"
"""

leave_msg = leave_msg + "\n" + add_

def banned(user_id: str) -> bool:
    banned_data: Union[BannedList, Any] = group_db.where_one(BannedList(), default=BannedList())
    banned: List[Dict[str, str]] = banned_data.banned_list
    for one in banned:
        if one["uid"] == user_id:
            return True
    return False


ban = on_command("ban", force_whitespace=True, priority=5)  # 封禁，≥10的用户无视封禁。


@ban.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10):
        await ban.finish(error(10))
    sb = args.extract_plain_text()
    self_protection = False
    if sb in Config.bot_basic.bot_owner:
        await ban.send("不能封禁机器人主人，这么玩就不好了，所以我先把你ban了QwQ")
        sb = str(event.user_id)
        self_protection = True
    if not sb:
        await ban.finish("您输入了什么？")
    elif not check_number(sb):
        await ban.finish("不能全域封禁不是纯数字的QQ哦~")
    elif banned(sb):
        return ban.finish("唔……全域封禁失败，这个人已经被封禁了。")
    else:
        current_data: Union[BannedList, Any] = group_db.where_one(BannedList(), default=BannedList())
        current = current_data.banned_list
        current.append({
            "uid": sb,
            "reason": ""
        })
        current_data.banned_list = current
        group_db.save(current_data)
        if self_protection:
            return
        await ban.finish(f"好的，已经全域封禁({sb})。")

unban = on_command("unban", force_whitespace=True, priority=5)  # 解封


@unban.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10):
        await ban.finish(error(10))
    sb = args.extract_plain_text()
    if check_number(sb) is False:
        await ban.finish("不能全域封禁不是纯数字的QQ哦~")
    if sb is False:
        await unban.finish("您输入了什么？")
    if banned(sb) is False:
        await unban.finish("全域解封失败，并没有封禁此人哦~")
    current_data: Union[BannedList, Any] = group_db.where_one(BannedList(), default=BannedList())
    current = current_data.banned_list
    for one in current:
        if one["uid"] == sb:
            current.remove(one)
    current_data.banned_list = current
    group_db.save(current_data)
    await ban.finish(f"好的，已经全域解封({sb})。")


@preprocess.handle()
async def _(matcher: Matcher, event: MessageEvent):
    current: Union[BannedList, Any] = group_db.where_one(BannedList(), default=BannedList())
    for i in current.banned_list:
        if str(event.user_id) == i["uid"] and not checker(str(event.user_id),10):
            matcher.stop_propagation()


dismiss = on_command("dismiss", aliases={"移除音卡"}, force_whitespace=True, priority=5)


@dismiss.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    user_permission = personal_data["role"] in ["owner", "admin"]
    if not (checker(str(event.user_id), 10) or user_permission):
        await dismiss.finish(f"唔……只有群主或管理员才能移除{Config.bot_basic.bot_name}哦~")
    else:
        await dismiss.send(f"确定要让{Config.bot_basic.bot_name}离开吗？如果是，请再发送一次“移除音卡”。")


@dismiss.got("confirm")
async def _(bot: Bot, event: GroupMessageEvent, confirm: Message = Arg()):
    u_input = confirm.extract_plain_text()
    if u_input == "移除音卡":
        await dismiss.send(leave_msg)
        await bot.call_api("send_group_msg", group_id=int(Config.bot_basic.bot_notice[str(event.self_id)]), message=f"{Config.bot_basic.bot_name}按他们的要求，离开了{event.group_id}。")
        await bot.call_api("set_group_leave", group_id=event.group_id)


recovery = on_command("recovery", aliases={"重置音卡"}, force_whitespace=True, priority=5)

@recovery.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    user_permission = personal_data["role"] in ["owner", "admin"]
    if not (checker(str(event.user_id), 10) or user_permission):
        await recovery.finish(f"唔……只有群主或管理员才能重置{Config.bot_basic.bot_name}哦~")
    else:
        await recovery.send(f"确定要重置{Config.bot_basic.bot_name}数据吗？如果是，请再发送一次“重置音卡”。\n注意：所有本群数据将会清空，包括绑定和订阅，该操作不可逆！")

@recovery.got("confirm")
async def _(bot: Bot, event: GroupMessageEvent, confirm: Message = Arg()):
    u_input = confirm.extract_plain_text()
    if u_input == "重置音卡":
        group_id = str(event.group_id)
        group_settings: Union[GroupSettings, Any] = group_db.where_one(GroupSettings(), "group_id = ?", group_id, default=None)
        group_settings = GroupSettings(id=group_settings.id, group_id=group_settings.group_id)
        group_db.save(group_settings)
        await dismiss.send("重置成功！可以重新开始绑定本群数据了！")