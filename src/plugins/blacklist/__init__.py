from pathlib import Path
from typing import Union, Any

from nonebot import on_command
from nonebot.adapters import Message, Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.tools.permission import checker
from src.tools.database import group_db, GroupSettings
from src.tools.utils.file import read, write
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.generate import get_uuid, generate

block = on_command("block", aliases={"避雷", "加入黑名单"}, force_whitespace=True, priority=5)  # 综合避雷名单-添加


@block.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    permission = checker(str(event.user_id), 5)
    if not permission and not group_admin:
        await block.finish("唔……只有群主或管理员才能修改哦~")
    if len(arg) != 2:
        await block.finish("唔……需要2个参数，第一个参数为玩家名，第二个参数是原因~\n提示：理由中请勿包含空格。")
    sb = arg[0]
    reason = arg[1]
    new = {"ban": sb, "reason": reason}
    group_id = str(event.group_id)
    current_data: Union[GroupSettings, Any] = group_db.where_one(GroupSettings(), "group_id = ?", group_id, default=GroupSettings())
    current_blacklist = current_data.blacklist
    for i in current_blacklist:
        if i["ban"] == sb:
            await block.finish("该玩家已加入黑名单，请勿重复添加，如需更新理由可以先移除再重新添加。")
    current_blacklist.append(new)
    current_data.blacklist = current_blacklist
    group_db.save(current_data)
    await block.finish("成功将该玩家加入黑名单！")

unblock = on_command("unblock", aliases={"移出黑名单"}, force_whitespace=True, priority=5)  # 解除避雷

@unblock.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    permission = checker(str(event.user_id), 5)
    if not permission and not group_admin:
        await block.finish("唔……只有群主或管理员才能修改哦~")
    if len(arg) != 1:
        await unblock.finish("参数仅为玩家名，请勿附带任何信息！")
    sb = arg[0]
    group_id = str(event.group_id)
    current_data: Union[GroupSettings, Any] = group_db.where_one(GroupSettings(), "group_id = ?", group_id, default=GroupSettings(group_id=str(event.group_id)))
    current_blacklist = current_data.blacklist
    for i in current_blacklist:
        if i["ban"] == sb:
            current_blacklist.remove(i)
            current_data.blacklist = current_blacklist
            group_db.save(current_data)
            await unblock.finish("成功移除该玩家的避雷！")
    await unblock.finish("移除失败！尚未避雷该玩家！")

sblock = on_command("sblock", aliases={"查找黑名单"}, force_whitespace=True, priority=5)  # 查询是否在避雷名单

@sblock.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 1:
        await sblock.finish("参数仅为玩家名，请勿附带任何信息！")
    sb = arg[0]
    group_id = str(event.group_id)
    current_data: Union[GroupSettings, Any] = group_db.where_one(GroupSettings(), "group_id = ?", group_id, default=GroupSettings(group_id=str(event.group_id)))
    current_blacklist = current_data.blacklist
    for i in current_blacklist:
        if i["ban"] == sb:
            reason = i["reason"]
            msg = f"玩家[{sb}]被避雷的原因为：\n{reason}"
            await sblock.finish(msg)
    await sblock.finish("该玩家没有被本群加入黑名单哦~")


template = """
<tr>
    <td class="short-column">$name</td>
    <td class="short-column">$reason</td>
</tr>"""

lblock = on_command("lblock", aliases={"本群黑名单", "列出黑名单"}, force_whitespace=True, priority=5)  # 列出所有黑名单


@lblock.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    group_id = str(event.group_id)
    current_data: Union[GroupSettings, Any] = group_db.where_one(GroupSettings(), "group_id = ?", group_id, default=GroupSettings(group_id=str(event.group_id)))
    current_blacklist = current_data.blacklist
    table = []
    if len(current_blacklist) == 0:
        await lblock.finish("唔……本群没有设置任何避雷名单哦~")
    for i in current_blacklist:
        table.append(template.replace("$name", i["ban"]).replace("$reason", i["reason"]))
    final_table = "\n".join(table)
    html = read(VIEWS + "/jx3/blacklist/blacklist.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    if not isinstance(final_path, str):
        return
    send_path = Path(final_path).as_uri()
    await lblock.finish(ms.image(send_path))