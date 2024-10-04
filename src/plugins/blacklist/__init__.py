from pathlib import Path
from jinja2 import Template

from nonebot import on_command
from nonebot.adapters import Message, Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.utils.database.operation import get_group_settings
from src.utils.permission import check_permission
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from .process import BlackList
from ._template import table_head, template_body

BlockMatcher = on_command(
    "block", 
    aliases={"避雷", "加入黑名单"}, 
    force_whitespace=True, 
    priority=5
)


@BlockMatcher.handle()
async def _(
    bot: Bot, 
    event: GroupMessageEvent, 
    full_argument: Message = CommandArg()
):
    if full_argument.extract_plain_text() == "":
        return
    args = full_argument.extract_plain_text().split(" ")
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    permission = check_permission(str(event.user_id), 5)
    if not permission and not group_admin:
        await BlockMatcher.finish("唔……只有群主或管理员才能修改哦~")
    if len(args) != 2:
        await BlockMatcher.finish("唔……需要2个参数，第一个参数为玩家名，第二个参数是原因~\n提示：理由中请勿包含空格。")
    status = BlackList(args[0], event.group_id).add(args[1])
    if status:
        await BlockMatcher.finish("该玩家已加入黑名单，请勿重复添加，如需更新理由可以先移除再重新添加。")
    await BlockMatcher.finish("成功将该玩家加入黑名单！")

UnblockMatcher = on_command("unblock", aliases={"移出黑名单"}, force_whitespace=True, priority=5)  # 解除避雷

@UnblockMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    permission = check_permission(str(event.user_id), 5)
    if not permission and not group_admin:
        await BlockMatcher.finish("唔……只有群主或管理员才能修改哦~")
    if len(arg) != 1:
        await UnblockMatcher.finish("参数仅为玩家名，请勿附带任何信息！")
    status = BlackList(arg[0], event.group_id).remove()
    if not status:
        await UnblockMatcher.finish("移除失败！尚未避雷该玩家！")
    await UnblockMatcher.finish("移除避雷成功！")

SearchBlockMatcher = on_command("sblock", aliases={"查找黑名单"}, force_whitespace=True, priority=5)  # 查询是否在避雷名单

@SearchBlockMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 1:
        await SearchBlockMatcher.finish("参数仅为玩家名，请勿附带任何信息！")
    status = BlackList(arg[0], event.group_id).status
    if not status:
        await SearchBlockMatcher.finish("该玩家没有被本群加入黑名单哦~")
    await SearchBlockMatcher.finish(f"该玩家被避雷的原因是：\n{status}")


ListBlockMatcher = on_command("lblock", aliases={"本群黑名单", "列出黑名单"}, force_whitespace=True, priority=5)  # 列出所有黑名单


@ListBlockMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    current_blacklist = get_group_settings(event.group_id, "blacklist")
    if len(current_blacklist) == 0:
        await ListBlockMatcher.finish("唔……本群没有设置任何避雷名单哦~")
    table = []
    for i in current_blacklist:
        table.append(
            Template(template_body).render(
                name = i["ban"],
                reason = i["reason"]
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = f" · 避雷名单 · {event.group_id}",
            table_head = table_head,
            table_body = "\n".join(table)
        )
    )
    final_path = await generate(html, "table", False)
    if not isinstance(final_path, str):
        return
    send_path = Path(final_path).as_uri()
    await ListBlockMatcher.finish(ms.image(send_path))