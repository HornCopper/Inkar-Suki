from src.tools.dep import *
from nonebot import on_command, on_request
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, RequestEvent

util_cmd_handle_request = on_command(
    "util_handle_request",
    name="处理领养申请",
    aliases={"处理申请"},
    priority=5,
    description="",
    catalog=permission.bot.group.apply,
    example=[
        Jx3Arg(Jx3ArgsType.group_id, is_optional=True),
        Jx3Arg(Jx3ArgsType.bool, is_optional=True),
        Jx3Arg(Jx3ArgsType.remark, is_optional=True)
    ],
    document="""获取当前待处理的申请，选择要处理领养申请处理"""
)

current_requests: dict[str, dict[str, dict]] = filebase_database.Database(
    f"{bot_path.common_data_full}group_requests").value


@util_cmd_handle_request.handle()
async def util_handle_request(bot: Bot, event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    group_id, accept, reason = args
    user_id = event.user_id
    if not group_id:
        return await view_requests(str(bot.self_id))
    return await handle_request(bot, str(user_id),  str(group_id), accept, reason)


async def view_requests(self_id: str):
    global current_requests
    self_id = str(self_id)  # 似乎nb传回的类型不稳定
    cur_items = current_requests.get(str(self_id)) or {}
    cur_items = [cur_items[x] for x in list(cur_items)]
    cur_items.sort(key=lambda x: -DateTime(x.get("time")).timestamp())  # 看最近的
    result = ["当前待处理的群："]
    t = x.get("time")
    g = x.get("group_id")
    c = x.get("comment")
    result += [f"{DateTime().toRelativeTime(t)} 群{g} {c}" for x in cur_items]
    return await util_cmd_handle_request.send(str.join("\n", result))


async def handle_request(bot: Bot, user_id: str, group_id: str, accept: bool, reason: str):
    global current_requests
    self_id = str(bot.self_id)  # 似乎nb传回的类型不稳定
    group_id = str(group_id)
    user_id = str(user_id)
    if checker(user_id, 10) == False:
        await util_cmd_handle_request.finish(error(10))
    cur_items = current_requests.get(str(self_id))
    request_info = None if cur_items is None else cur_items.get(group_id)
    logger.debug(f"request_info:{request_info}")
    if not request_info:
        return await util_cmd_handle_request.finish(f"唔……处理失败，当前没有群号为「{group_id}」的申请")
    del cur_items[group_id]  # 处理完成，移除本记录
    try:
        await bot.set_group_add_request(
            flag=request_info.get("flag"),
            sub_type=request_info.get("sub_type"),
            approve=accept,
            reason=reason,
        )
    except Exception as ex:
        await util_cmd_handle_request.finish(f"处理失败，音卡记录下了报错内容：\n{ex}")
    msg = ""
    msg_reason = f"\n附加消息：{reason}" if reason else ""
    await util_cmd_handle_request.finish(f"{msg}{msg_reason}")

util_cmd_on_group_invite = on_request(priority=5)


@util_cmd_on_group_invite.handle()
async def util_on_group_invite(bot: Bot, event: RequestEvent):
    """申请入群记录到待处理"""
    global current_requests
    if not event.request_type == "group":
        return
    if not event.sub_type == "invite":
        return
    group_id = str(event.group_id)
    self_id = str(event.self_id)

    data = {
        "self_id": event.self_id,
        "group_id": group_id,

        "flag": event.flag,
        "sub_type": event.sub_type,

        "comment": event.comment,
        "time": event.time,
    }
    if not current_requests.get(self_id):
        current_requests[self_id] = {}
    cur_items = current_requests[self_id]
    cur_items[group_id] = data
    logger.info(f"加群申请:已加入待处理列表:{data}")
