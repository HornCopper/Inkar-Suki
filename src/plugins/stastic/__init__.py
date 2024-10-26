from typing import Any
from jinja2 import Template
from pathlib import Path
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment as ms

from src.utils.message import message_universal
from src.utils.database import cache_db
from src.utils.database.classes import GroupMessage, MemberMessage
from src.utils.time import Time
from src.utils.network import Request
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from .utils import get_date_timestamp
from ._template import template_body, table_head

today_message_count = on_command("today_message_count", aliases={"本群发言统计"}, priority=5)

@today_message_count.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    start, end = get_date_timestamp(args.extract_plain_text())
    group_data: list[GroupMessage] | Any = cache_db.where_all(GroupMessage(), "group_id = ?", event.group_id, default=[])
    if len(group_data) == 0:
        await today_message_count.finish("唔……目前没有任何发言记录！")
    group_member_data: list[dict] = await bot.call_api("get_group_member_list", group_id=event.group_id)
    data = dict(
        sorted(
            {
                str(m.user_id): [d for d in m.messages if start <= d.timestamp <= end] 
                for m
                in group_data
            }.items(),
            key=lambda item: len(item[1]),
            reverse=True
        )
    )
    if all(value == [] for value in data.values()):
        await today_message_count.finish("唔……没有该时间段的发言记录！")
    num = 0
    table = []
    for each_data in data.items():
        user_id, msgs = each_data
        msg_count = len(msgs)
        if msg_count == 0:
            continue
        member_data: list[dict] = [g for g in group_member_data if g["user_id"] == int(user_id)]
        if len(member_data) != 1:
            continue
        nickname: str = member_data[0]["nickname"]
        num += 1
        table.append(
            Template(
                template_body
            ).render(
                rank = str(num),
                avatar = f"https://q.qlogo.cn/headimg_dl?dst_uin={user_id}&spec=100&img_type=jpg",
                nickname = nickname,
                user_id = user_id,
                count = msg_count
            )
        )
        if num == 50:
            break
    html = str(
        HTMLSourceCode(
            application_name=f" · 发言统计 · {event.group_id}",
            table_head=table_head,
            table_body="\n".join(table)
        )
    )
    final_path = await generate(html, "table", False)
    if not isinstance(final_path, str):
        return
    image = Request(Path(final_path).as_uri()).local_content
    await today_message_count.finish(ms.image(image))
    
    

@message_universal.handle()
async def _(event: GroupMessageEvent):
    group_data: GroupMessage | Any = cache_db.where_one(
        GroupMessage(),
        "group_id = ? AND user_id = ?",
        event.group_id,
        event.user_id,
        default=GroupMessage(
            group_id=event.group_id,
            user_id=event.user_id
        )
    )
    msg_list = group_data.messages
    msg_list.append(
        MemberMessage(timestamp=Time().raw_time)
    )
    group_data.messages = msg_list
    cache_db.save(group_data)