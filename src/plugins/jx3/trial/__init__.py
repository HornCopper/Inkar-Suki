from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

from src.const.jx3.kungfu import Kungfu
from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.analyze import check_number

from .api import get_trial_dps, get_trial_rank


trial_rank_matcher = on_command("jx3_slrank", aliases={"试炼之地", "试炼"}, priority=5, force_whitespace=True)


@trial_rank_matcher.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if msg.extract_plain_text() == "":
        return
    args = msg.extract_plain_text().strip().split(" ")
    if len(args) not in [1, 2]:
        await trial_rank_matcher.finish(PROMPT.ArgumentCountInvalid)
    if len(args) == 1:
        server = Server(None, event.group_id).server
        kungfu_name = args[0]
    elif args[0] == "全服":
        server = ""
        kungfu_name = args[1]
    else:
        server = Server(args[0], event.group_id).server
        kungfu_name = args[1]
    kungfu_name = Kungfu(kungfu_name).name
    if kungfu_name is None:
        await trial_rank_matcher.finish(PROMPT.SchoolInvalid)
    if server is None:
        await trial_rank_matcher.finish(PROMPT.ServerNotExist)
    await trial_rank_matcher.finish(await get_trial_rank(kungfu_name, server))


trial_dps_matcher = on_command("jx3_trial_dps", aliases={"试炼秒伤"}, priority=5, force_whitespace=True)


@trial_dps_matcher.handle()
async def _(args: Message = CommandArg()):
    usage = "参考格式：试炼秒伤 <层数>\n示例：试炼秒伤 100"
    query = args.extract_plain_text().strip()
    if not check_number(query) or not float(query).is_integer():
        await trial_dps_matcher.finish(PROMPT.ArgumentCountInvalid + "\n" + usage)
    floor = int(float(query))
    if floor <= 0:
        await trial_dps_matcher.finish("试炼层数必须为正整数！\n" + usage)
    await trial_dps_matcher.finish(await get_trial_dps(floor))
