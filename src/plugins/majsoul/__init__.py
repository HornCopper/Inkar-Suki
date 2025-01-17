from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from .koromo import find_player, get_records, player_pt
from .monthly_report import MSMRG

import re

MSSearchPlayerMatcher = on_command("mssp", priority=5, force_whitespace=True)

@MSSearchPlayerMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    data = await find_player(args.extract_plain_text())
    await MSSearchPlayerMatcher.finish(data)


MSGameRecordMatcher = on_command("msgr", priority=5, force_whitespace=True)

@MSGameRecordMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    data = await get_records(args.extract_plain_text())
    await MSGameRecordMatcher.finish(data)


MSGetPTMatcher = on_command("mspt", priority=5, force_whitespace=True)

@MSGetPTMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    data = await player_pt(args.extract_plain_text())
    await MSGetPTMatcher.finish(data)

MSMonthReport = on_command("msmr", priority=5, force_whitespace=True)

@MSMonthReport.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().strip().split(" ")
    if len(arg) not in [1, 2]:
        await MSMonthReport.finish("格式错误！\nmsmr 玩家名 [月份]\n月份格式：2024-11")
    if len(arg) == 1:
        generator = await MSMRG.with_role_name(arg[0])
    elif len(arg) == 2:
        if not bool(re.match(r"^\d{4}-\d{2}$", arg[1])):
            await MSMonthReport.finish("月份格式错误！请给出yyyy-mm的格式！")
        generator = await MSMRG.with_role_name(arg[0], arg[1])
    if isinstance(generator, str):
        await MSMonthReport.finish(generator)
    else:
        image = await generator.generate_image()
        await MSMonthReport.finish(image)