from src.tools.dep import *
from .assistance import Assistance

aic = Assistance

create = on_command("创建团队", priority=5)


@create.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    resp = await aic.create_group(str(event.group_id), args.extract_plain_text(), str(event.user_id))
    return await create.finish(resp)

apply = on_command("预定", aliases={"预订", "报名"}, priority=5)


@apply.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    args = args.extract_plain_text().split(" ")
    if len(args) != 3:
        return await apply.finish("请检查命令后，重试哦~\n格式为：预定 <团队关键词> <ID> <职业>")
    else:
        keyword = args[0]
        id = args[1]
        job = args[2]
        resp = await aic.apply_for_place(str(event.group_id), keyword, id, job, str(event.user_id))
        return await apply.finish(resp)

disapply = on_command("取消预定", aliases={"取消预订", "取消报名"}, priority=5)


@disapply.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    args = args.extract_plain_text().split(" ")
    if len(args) != 2:
        return await disapply.finish("请检查命令后，重试哦~\n格式为：取消预定 <团队关键词> <ID>")
    else:
        keyword = args[0]
        id = args[1]
        resp = await aic.cancel_apply(str(event.group_id), keyword, id, str(event.user_id))
        return await disapply.finish(resp)

dissolve = on_command("解散团队", aliases={"取消开团"}, priority=5)


@dissolve.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    keyword = args.extract_plain_text()
    if keyword == "":
        return await dissolve.finish("唔……没有输入关键词哦，请检查后重试~")
    resp = await aic.dissolve(str(event.group_id), keyword, str(event.user_id))
    return await dissolve.finish(resp)

team = on_command("查看团队", priority=5)


@team.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    keyword = args.extract_plain_text()
    if keyword == "":
        return await team.finish("唔……没有输入关键词哦，请检查后重试~")
    html_path = await aic.generate_html(str(event.group_id), keyword)
    img = await generate(html_path, False, "table", False)
    return await team.finish(ms.image(Path(img).as_uri()))

rd = on_command("随机抽取", priority=5)


@rd.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    keyword = args.extract_plain_text()
    if keyword == "":
        return await rd.finish("唔……没有输入关键词哦，请检查后重试~")
    return await rd.finish(await aic.random_member(str(event.group_id), keyword))
