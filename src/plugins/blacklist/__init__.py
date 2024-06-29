from src.tools.basic import *


block = on_command("block", aliases={"避雷", "加入黑名单"}, force_whitespace=True, priority=5)  # 综合避雷名单-添加


@block.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
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
    now = json.loads(read(DATA + "/" + str(event.group_id) + "/blacklist.json"))
    for i in now:
        if i["ban"] == sb:
            await block.finish("该玩家已加入黑名单。")
    now.append(new)
    write(DATA + "/" + str(event.group_id) + "/blacklist.json", json.dumps(now, ensure_ascii=False))
    await block.finish("成功将该玩家加入黑名单！")

unblock = on_command("unblock", aliases={"移出黑名单"}, force_whitespace=True, priority=5)  # 解除避雷

@unblock.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
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
    now = json.loads(read(DATA + "/" + str(event.group_id) + "/blacklist.json"))
    for i in now:
        if i["ban"] == sb:
            now.remove(i)
            write(DATA + "/" + str(event.group_id) + "/blacklist.json",
                  json.dumps(now, ensure_ascii=False))
            await unblock.finish("成功移除该玩家的避雷！")
    await unblock.finish("移除失败！尚未避雷该玩家！")

sblock = on_command("sblock", aliases={"查找黑名单"}, force_whitespace=True, priority=5)  # 查询是否在避雷名单

@sblock.handle()
async def _(event: Event, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 1:
        await sblock.finish("参数仅为玩家名，请勿附带任何信息！")
    sb = arg[0]
    now = json.loads(read(DATA + "/" + str(event.group_id) + "/blacklist.json"))
    for i in now:
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
    now = json.loads(read(DATA + "/" + str(event.group_id) + "/blacklist.json"))
    table = []
    if len(now) == 0:
        await lblock.finish("唔……本群没有设置任何避雷名单哦~")
    for i in now:
        table.append(template.replace("$name", i["ban"]).replace("$reason", i["reason"]))
    final_table = "\n".join(table)
    html = read(VIEWS + "/jx3/blacklist/blacklist.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    saohua = saohua["data"]["text"]
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    send_path = Path(final_path).as_uri()
    await lblock.finish(ms.image(send_path))
    
