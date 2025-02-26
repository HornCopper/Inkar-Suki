from jinja2 import Template

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, Bot
from nonebot.params import CommandArg

from src.utils.database.operation import get_group_settings
from src.utils.permission import check_permission
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from .process import Blacklist
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
    if len(args) != 2:
        await BlockMatcher.finish("唔……需要2个参数，第一个参数为玩家名，第二个参数是原因~\n提示：理由中请勿包含空格。")
    status = Blacklist(args[0], event.group_id).add(args[1])
    if status:
        await BlockMatcher.finish("该玩家已加入黑名单，请勿重复添加，如需更新理由可以先移除再重新添加。")
    await BlockMatcher.finish("成功将该玩家加入黑名单！")

UnblockMatcher = on_command("unblock", aliases={"移除黑名单", "移出黑名单", "删除避雷", "撤销避雷", "取消避雷"}, force_whitespace=True, priority=5)  # 解除避雷

@UnblockMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 1:
        await UnblockMatcher.finish("参数仅为玩家名，请勿附带任何信息！")
    status = Blacklist(arg[0], event.group_id).remove()
    if not status:
        await UnblockMatcher.finish("移除失败！尚未避雷该玩家！")
    await UnblockMatcher.finish("移除避雷成功！")

ListBlockMatcher = on_command("lblock", aliases={"本群黑名单", "列出黑名单", "黑名单", "避雷名单"}, force_whitespace=True, priority=5)  # 列出所有黑名单

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
    image = await generate(html, "table", segment=True)
    await ListBlockMatcher.finish(image)