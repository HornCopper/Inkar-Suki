from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.utils.analyze import check_number
from src.utils.network import Request
from src.utils.database.operation import get_group_settings

from .app import Assistance

AssistanceInstance = Assistance()

CreateTeamMatcher = on_command("创建团队", force_whitespace=True, priority=5)

@CreateTeamMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if check_number(args.extract_plain_text()):
        await CreateTeamMatcher.finish("唔……请勿使用纯数字作为关键词！")
    resp = await AssistanceInstance.create_group(str(event.group_id), args.extract_plain_text(), str(event.user_id))
    await CreateTeamMatcher.finish(resp)

BookTeamMatcher = on_command("预定", aliases={"预订", "报名"}, force_whitespace=True, priority=5)

@BookTeamMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 3:
        await BookTeamMatcher.finish("请检查命令后，重试哦~\n格式为：预定 <团队关键词> <ID> <职业>")
    else:
        keyword = arg[0]
        id = arg[1]
        job = arg[2]
        resp = await AssistanceInstance.apply_for_place(str(event.group_id), keyword, id, job, str(event.user_id))
        await BookTeamMatcher.finish(resp)

CancelTeamMatcher = on_command("取消预定", aliases={"取消预订", "取消报名"}, force_whitespace=True, priority=5)

@CancelTeamMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await CancelTeamMatcher.finish("请检查命令后，重试哦~\n格式为：取消预定 <团队关键词> <ID>")
    else:
        keyword = arg[0]
        id = arg[1]
        resp = await AssistanceInstance.cancel_apply(str(event.group_id), keyword, id, str(event.user_id))
        await CancelTeamMatcher.finish(resp)

DissolveTeamMatcher = on_command("解散团队", aliases={"取消开团"}, force_whitespace=True, priority=5)

@DissolveTeamMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    keyword = args.extract_plain_text()
    if keyword == "":
        await DissolveTeamMatcher.finish("唔……没有输入关键词哦，请检查后重试~")
    resp = await AssistanceInstance.dissolve(str(event.group_id), keyword, str(event.user_id))
    await DissolveTeamMatcher.finish(resp)

LookupTeamMatcher = on_command("查看团队", priority=5, force_whitespace=True)

@LookupTeamMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    keyword = args.extract_plain_text()
    if keyword == "":
        await LookupTeamMatcher.finish("唔……没有输入关键词哦，请检查后重试~")
    img_path = await AssistanceInstance.generate_html(str(event.group_id), keyword)
    if not isinstance(img_path, str):
        return
    img = Request(img_path).local_content
    await LookupTeamMatcher.finish(ms.image(img))

TeamListMatcher = on_command("团队列表", priority=5, force_whitespace=True)

@TeamListMatcher.handle()
async def _(event: GroupMessageEvent):
    file_content = get_group_settings(str(event.group_id), "opening")
    if not isinstance(file_content, list):
        return
    if len(file_content) == 0:
        await TeamListMatcher.finish("唔……本群没有任何团队！")
    msg = "本群有以下团队：\n"
    for i in range(len(file_content)):
        msg += str(i) + ". " + file_content[i]["description"] + "\n创建者：" + str(file_content[i]["creator"]) + "\n"
    await TeamListMatcher.finish(msg[:-1])