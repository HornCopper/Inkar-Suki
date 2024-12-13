from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg

from src.const.prompts import PROMPT
from src.utils.analyze import check_number
from src.utils.database.operation import get_group_settings, set_group_settings

from .app import Assistance, parse_limit, get_answer

AssistanceInstance = Assistance()

CreateTeamMatcher = on_command("创建团队", force_whitespace=True, priority=5)

@CreateTeamMatcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    if argument.extract_plain_text() == "":
        return
    if check_number(argument.extract_plain_text()):
        await CreateTeamMatcher.finish("唔……请勿使用纯数字作为关键词！")
    args = argument.extract_plain_text().split(" ")
    if not parse_limit(args[-1]):
        team_name = argument.extract_plain_text()
        resp = AssistanceInstance.create_group(str(event.group_id), team_name, str(event.user_id))
    else:
        team_name = " ".join(args[:-1])
        team_limit = args[-1]
        resp = AssistanceInstance.create_group(str(event.group_id), team_name, str(event.user_id), team_limit)
    await CreateTeamMatcher.finish(resp)

BookTeamMatcher = on_command("预定", aliases={"预订", "报名"}, force_whitespace=True, priority=5)

@BookTeamMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().strip().split(" ")
    if len(arg) not in [2, 3]:
        await BookTeamMatcher.finish("请检查命令后，重试哦~\n格式为：预定 <团队关键词/序号> <职业> <ID>\n若当前只有一个团队进行，可以省略关键词或序号！")
    if len(arg) == 3:
        keyword = arg[0]
        job = arg[1]
        id = arg[2]
    elif len(arg) == 2:
        keyword = "1" if len(get_group_settings(event.group_id, "opening")) == 1 else False
        job = arg[0]
        id = arg[1]
    if not keyword:
        await BookTeamMatcher.finish("当前进行中的团队超过1个，请携带团队关键词/序号！")
    resp = AssistanceInstance.apply_for_place(str(event.group_id), keyword, id, job, str(event.user_id))
    await BookTeamMatcher.finish(resp)

CancelTeamMatcher = on_command("取消预定", aliases={"取消预订", "取消报名"}, force_whitespace=True, priority=5)

@CancelTeamMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    unique = len(get_group_settings(event.group_id, "opening")) == 1
    if len(arg) not in [1, 2]:
        await CancelTeamMatcher.finish("请检查命令后，重试哦~\n格式为：取消预定 <团队关键词> <ID>")
    if len(arg) == 2:
        keyword = arg[0]
        id = arg[1]
    elif len(arg) == 1:
        if not unique:
            await CancelTeamMatcher.finish("当前进行中的团队超过1个，请携带团队关键词/序号！")
        keyword = "1"
        id = arg[0]
    resp = AssistanceInstance.cancel_apply(str(event.group_id), keyword, id, str(event.user_id))
    await CancelTeamMatcher.finish(resp)

DissolveTeamMatcher = on_command("解散团队", aliases={"取消开团"}, force_whitespace=True, priority=5)

@DissolveTeamMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    keyword = args.extract_plain_text()
    unique = len(get_group_settings(event.group_id, "opening")) == 1
    if keyword == "" and not unique:
        await DissolveTeamMatcher.finish("唔……没有输入关键词哦，请检查后重试~")
    if keyword == "" and unique:
        keyword = "1"
    resp = AssistanceInstance.dissolve(str(event.group_id), keyword, str(event.user_id))
    await DissolveTeamMatcher.finish(resp)

LookupTeamMatcher = on_command("查看团队", priority=5, force_whitespace=True)

@LookupTeamMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    keyword = args.extract_plain_text()
    unique = len(get_group_settings(event.group_id, "opening")) == 1
    if keyword == "" and not unique:
        await LookupTeamMatcher.finish("唔……没有输入关键词哦，请检查后重试~")
    if keyword == "" and unique:
        keyword = "1"
    image = await AssistanceInstance.generate_html(str(event.group_id), keyword)
    await LookupTeamMatcher.finish(image)

TeamlistMatcher = on_command("团队列表", priority=5, force_whitespace=True)

@TeamlistMatcher.handle()
async def _(event: GroupMessageEvent):
    all_teams = get_group_settings(str(event.group_id), "opening")
    if not isinstance(all_teams, list):
        return
    if len(all_teams) == 0:
        await TeamlistMatcher.finish("唔……本群没有任何团队！")
    msg = "本群有以下团队：\n"
    for i in range(len(all_teams)):
        name = all_teams[i]["description"]
        leader = str(all_teams[i]["creator"])
        if "limit" not in all_teams[i]:
            limit = "无"
        else:
            parsed_limit = parse_limit(all_teams[i]["limit"])
            if not parsed_limit:
                limit = "无"
            else:
                limit = all_teams[i]["limit"]
        msg += str(i + 1) + ". " + name + "\n创建者：" + leader + "\n职业限制：" + limit + "\n"
    await TeamlistMatcher.finish(msg[:-1])

ShareTeamMatcher = on_command("共享团队", priority=5, force_whitespace=True)

@ShareTeamMatcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    args = argument.extract_plain_text().split(" ")
    if len(args) != 2:
        await ShareTeamMatcher.finish(PROMPT.ArgumentCountInvalid)
    group_id = args[0]
    keyword = args[1]
    if not check_number(group_id):
        await ShareTeamMatcher.finish("唔……检测到群号非数字，共享团队失败，请检查后重试！")
    status = AssistanceInstance.share_team(int(group_id), event.group_id, keyword, event.user_id)
    if not status:
        await ShareTeamMatcher.finish("共享团队失败！请检查源群是否有该团队，以及是否为您创建，关键词是否正确，然后重试！")
    await ShareTeamMatcher.finish("已共享团队至本群！")

ModifyLimitMatcher = on_command("修改团队限制", priority=5, force_whitespace=True)

@ModifyLimitMatcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    args = argument.extract_plain_text().split(" ")
    if len(args) != 2:
        await ModifyLimitMatcher.finish(PROMPT.ArgumentCountInvalid)
    keyword = args[0]
    limit = args[1]
    if limit != "无" and not parse_limit(limit):
        await ModifyLimitMatcher.finish("无法解析您的限制！请参考下面的示例：\n修改团队限制 3T5N15D1B\n该词条代表，3防御5治疗15输出1老板")
    if limit == "无":
        limit = ""
    teams: list[dict] = get_group_settings(event.group_id, "opening")
    for each_team in teams:
        if each_team["creator"] == str(event.user_id) and (str(teams.index(each_team) + 1) == keyword or each_team["description"] == keyword):
            each_team["limit"] = limit
            set_group_settings(event.group_id, "opening", teams)
            await ModifyLimitMatcher.finish("修改限制成功，下次报名将会检查是否满足该限制！")
    await ModifyLimitMatcher.finish("未找到该序号/关键词且为您创建的团队，请检查后重试！")

YZKSecretMatcher = on_command("解密", aliases={"解谜", "揭秘"}, priority=5)

@YZKSecretMatcher.handle()
async def _(event: GroupMessageEvent):
    msg = get_answer()
    await YZKSecretMatcher.finish(msg)