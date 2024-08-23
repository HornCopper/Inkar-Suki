from typing import Union, Any

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.params import CommandArg
from nonebot.adapters import Message

from src.tools.permission import checker, error
from src.tools.database import group_db, ApplicationsList
from src.tools.utils.time import convert_time
from src.tools.utils.num import checknumber

current_application = on_command("邀请列表", force_whitespace=True, priority=5)


@current_application.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    if not checker(str(event.user_id), 10):
        await current_application.finish(error(10))
    current_data: Union[ApplicationsList, Any] = group_db.where_one(ApplicationsList(), default=ApplicationsList())
    current_applications = current_data.applications_list
    prefix = "当前有下列群聊可以处理：\n"
    msgs = []
    for i in current_applications:
        group = str(i["group_id"])
        user = str(i["user_id"])
        time_ = convert_time(i["time"], "%m-%d %H:%M:%S")
        msg = f"群聊（{group}），由{user}发起，日期为：{time_}"
        msgs.append(msg)
    await current_application.finish(prefix + "\n".join(msgs))


process_application = on_command("同意邀请", aliases={"同意申请"}, force_whitespace=True, priority=5)


@process_application.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10):
        await process_application.finish(error(10))
    arg = args.extract_plain_text()
    if not checknumber(arg):
        await process_application.finish("唔……同意申请的命令后面直接加群号即可哦~")
    current_data: Union[ApplicationsList, Any] = group_db.where_one(ApplicationsList(), default=ApplicationsList())
    current_applications = current_data.applications_list
    flag = False
    for i in current_applications:
        if i["group_id"] == int(arg):
            await bot.call_api("set_group_add_request", flag=i["flag"], sub_type="invite", approve=True)
            await process_application.send("已经将该群聊的申请处理完毕啦，音卡已经前往那里了！")
            flag = True
    if flag:
        for i in current_applications:
            if i["group_id"] == int(arg):
                current_applications.remove(i)
        return
    await process_application.finish("呜喵……真的有这个群申请了吗？")


deny_application = on_command("拒绝邀请", aliases={"拒绝邀请"}, force_whitespace=True, priority=5)


async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10):
        await deny_application.finish(error(10))
    arg = args.extract_plain_text()
    if not checknumber(arg):
        await deny_application.finish("唔……同意申请的命令后面直接加群号即可哦~")
    current_data: Union[ApplicationsList, Any] = group_db.where_one(ApplicationsList(), default=ApplicationsList())
    current_applications = current_data.applications_list
    for i in current_applications:
        if i["group_id"] == int(arg):
            await bot.call_api("set_group_add_request", flag=i["flag"], sub_type="invite", approve=True)
            await deny_application.send("音卡已拒绝该申请！")
            flag = True
    if flag:
        for i in current_applications:
            if i["group_id"] == int(arg):
                current_applications.remove(i)
        return
    await deny_application.finish("呜喵……真的有这个群申请了吗？")


donate = on_command("donate", aliases={"赞助音卡"}, force_whitespace=True, priority=5)


@donate.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    await donate.finish("感谢您对音卡的支持，点击下方链接可以支持音卡：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/donate\n请注意：音卡**绝对不是**付费，赞助全自愿！！")