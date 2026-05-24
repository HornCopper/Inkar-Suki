from pathlib import Path

from nonebot import on_command
from nonebot.params import CommandArg, Received
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageEvent, MessageSegment as ms
from nonebot.typing import T_State

from src.utils.network import Request

from .koromo import find_player, get_records, player_pt
from .monthly_report import MSMRG
from .guess_tenpai import generate_question, is_correct_answer, render_hand_image, tiles_to_code

import re


TENPAI_DIFFICULTY_ALIASES = {
    "简单": "simple",
    "easy": "simple",
    "simple": "simple",
    "困难": "hard",
    "难": "hard",
    "hard": "hard",
    "difficult": "hard",
    "清一色": "chinitsu",
    "清": "chinitsu",
    "chinitsu": "chinitsu",
    "flush": "chinitsu",
}

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


GuessTenpaiMatcher = on_command("猜听牌", priority=5, force_whitespace=True)


@GuessTenpaiMatcher.handle()
async def _(state: T_State, event: MessageEvent, args: Message = CommandArg()):
    difficulty_text = args.extract_plain_text().strip().lower()
    if difficulty_text == "":
        await GuessTenpaiMatcher.finish("请输入难度：猜听牌 [简单|困难|清一色]")
    difficulty = TENPAI_DIFFICULTY_ALIASES.get(difficulty_text)
    if difficulty is None:
        await GuessTenpaiMatcher.finish("参数错误，请使用：猜听牌 [简单|困难|清一色]")
    question = generate_question(difficulty)
    state["tenpai_waits"] = question.waits
    state["tenpai_hand_code"] = question.hand_code
    state["tenpai_difficulty"] = difficulty
    image_path = render_hand_image(question.hand)
    message = Message(ms.image(Request(Path(image_path).as_uri()).local_content))
    message += f"{question.hand_code}\n请回答听牌编码，例如：58p、5p8p、19m19s1234567z。"
    await GuessTenpaiMatcher.send(ms.at(event.user_id) + message)


@GuessTenpaiMatcher.receive("answer")
async def _(state: T_State, event: MessageEvent = Received("answer")):
    answer = event.message.extract_plain_text().strip()
    waits = state["tenpai_waits"]
    wait_code = tiles_to_code(waits)
    if is_correct_answer(answer, waits):
        await GuessTenpaiMatcher.finish(ms.at(event.user_id) + f" 回答正确！听牌：{wait_code}")
    await GuessTenpaiMatcher.finish(ms.at(event.user_id) + f"回答错误，正确答案：{wait_code}")
