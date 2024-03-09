from src.tools.basic import *

current_application = on_command("邀请列表", priority=5)

@current_application.handle()
async def _(event: Event):
    if os.path.exists(TOOLS + "/application.json") == False:
        write(TOOLS + "/application.json", "[]")
    if checker(str(event.user_id), 10) == False:
        await current_application.finish(error(10))
    current = json.loads(read(TOOLS + "/application.json"))
    prefix = "当前有下列群聊可以处理：\n"
    msgs = []
    for i in current:
        group = str(i["group_id"])
        user = str(i["user_id"])
        time_ = convert_time(i["time"], "%m-%d %H:%M:%S")
        msg = f"群聊（{group}），由{user}发起，日期为：{time_}"
        msgs.append(msg)
    await current_application.finish(prefix + "\n".join(msgs))
    

process_application = on_command("同意邀请", aliases={"同意申请"}, priority=5)

@process_application.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id), 10) == False:
        await process_application.finish(error(10))
    args = args.extract_plain_text()
    if checknumber(args) == False:
        await process_application.finish("唔……同意申请的命令后面直接加群号即可哦~")
    current = json.loads(read(TOOLS + "/application.json"))
    for i in current:
        if i["group_id"] == int(args):
            await bot.call_api("set_group_add_request", flag=i["flag"], sub_type="invite", approve=True)
            pre = current
            for x in pre:
                if x["group_id"] == int(args):
                    pre.remove(x)
            write(TOOLS + "/application.json", json.dumps(pre))
            await process_application.finish("已经将该群聊的申请处理完毕啦，音卡已经前往那里了！")
    await process_application.finish("呜喵……真的有这个群申请了吗？")


deny_application = on_command("拒绝邀请", aliases={"拒绝邀请"}, priority=5)
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id), 10) == False:
        await deny_application.finish(error(10))
    args = args.extract_plain_text()
    if checknumber(args) == False:
        await deny_application.finish("唔……同意申请的命令后面直接加群号即可哦~")
    current = json.loads(read(TOOLS + "/application.json"))
    for i in current:
        if i["group_id"] == int(args):
            await bot.call_api("set_group_add_request", flag=i["flag"], sub_type="invite", approve=False)
            pre = current
            for x in pre:
                if x["group_id"] == int(args):
                    pre.remove(x)
            write(TOOLS + "/application.json", json.dumps(pre))
            await deny_application.finish("已经将该群聊的申请处理完毕啦，音卡已经前往那里了！")
    await deny_application.finish("呜喵……真的有这个群申请了吗？")