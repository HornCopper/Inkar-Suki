from .api import *

aic = Assistance

create = on_command("创建团队", force_whitespace=True, priority=5)


@create.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if checknumber(args.extract_plain_text()):
        await create.finish("唔……请勿使用纯数字作为关键词！")
    resp = await aic.create_group(str(event.group_id), args.extract_plain_text(), str(event.user_id))
    await create.finish(resp)

apply = on_command("预定", aliases={"预订", "报名"}, force_whitespace=True, priority=5)


@apply.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    args = args.extract_plain_text().split(" ")
    if len(args) != 3:
        await apply.finish("请检查命令后，重试哦~\n格式为：预定 <团队关键词> <ID> <职业>")
    else:
        keyword = args[0]
        id = args[1]
        job = args[2]
        resp = await aic.apply_for_place(str(event.group_id), keyword, id, job, str(event.user_id))
        await apply.finish(resp)

disapply = on_command("取消预定", aliases={"取消预订", "取消报名"}, force_whitespace=True, priority=5)


@disapply.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    args = args.extract_plain_text().split(" ")
    if len(args) != 2:
        await disapply.finish("请检查命令后，重试哦~\n格式为：取消预定 <团队关键词> <ID>")
    else:
        keyword = args[0]
        id = args[1]
        resp = await aic.cancel_apply(str(event.group_id), keyword, id, str(event.user_id))
        await disapply.finish(resp)

dissolve = on_command("解散团队", aliases={"取消开团"}, force_whitespace=True, priority=5)


@dissolve.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    keyword = args.extract_plain_text()
    if keyword == "":
        await dissolve.finish("唔……没有输入关键词哦，请检查后重试~")
    resp = await aic.dissolve(str(event.group_id), keyword, str(event.user_id))
    await dissolve.finish(resp)

team = on_command("查看团队", priority=5, force_whitespace=True)


@team.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    keyword = args.extract_plain_text()
    if keyword == "":
        await team.finish("唔……没有输入关键词哦，请检查后重试~")
    img_path = await aic.generate_html(str(event.group_id), keyword)
    img = get_content_local(img_path)
    await team.finish(ms.image(img))


teamList = on_command("团队列表", priority=5, force_whitespace=True)

@teamList.handle()
async def _(event: GroupMessageEvent):
    file_content = json.loads(read(f"{DATA}/{str(event.group_id)}/opening.json"))
    if len(file_content) == 0:
        await teamList.finish("唔……本群没有任何团队！")
    msg = "本群有以下团队：\n"
    for i in range(len(file_content)):
        msg += str(i) + ". " + file_content[i]["description"] + "\n创建者：" + str(file_content[i]["creator"]) + "\n"
    await teamList.finish(msg + "小提示：序号可以替代关键词！")