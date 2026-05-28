from pathlib import Path
from dataclasses import dataclass

from nonebot import on_command, on_message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageEvent, MessageSegment as ms

from src.utils.network import Request

from .koromo import find_player, get_records, player_pt
from .monthly_report import MSMRG
from .guess_tenpai import generate_question, is_correct_answer, parse_tiles, render_hand_image, tiles_to_code

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
TENPAI_MAX_GUESSES = 5
TENPAI_NOTEN_ANSWERS = {"未听牌", "没听牌", "沒有听牌", "沒有聽牌", "未聽牌", "没聽牌", "noten"}


@dataclass
class TenpaiGame:
    waits: tuple[int, ...]
    hand_code: str
    difficulty: str
    attempts: dict[int, int]


active_tenpai_games: dict[str, TenpaiGame] = {}


def _tenpai_session_key(event: MessageEvent) -> str:
    if isinstance(event, GroupMessageEvent):
        return f"group:{event.group_id}"
    return f"private:{event.user_id}"


def _is_tenpai_answer_candidate(answer: str) -> bool:
    normalized_answer = answer.strip().lower().replace(" ", "")
    return normalized_answer in TENPAI_NOTEN_ANSWERS or parse_tiles(answer) is not None

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
GuessTenpaiAnswerMatcher = on_message(priority=6, block=False)


@GuessTenpaiMatcher.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    difficulty_text = args.extract_plain_text().strip().lower()
    if difficulty_text == "":
        await GuessTenpaiMatcher.finish("请输入难度：猜听牌 [简单|困难|清一色]")
    difficulty = TENPAI_DIFFICULTY_ALIASES.get(difficulty_text)
    if difficulty is None:
        await GuessTenpaiMatcher.finish("参数错误，请使用：猜听牌 [简单|困难|清一色]")
    question = generate_question(difficulty)
    active_tenpai_games[_tenpai_session_key(event)] = TenpaiGame(
        waits=question.waits,
        hand_code=question.hand_code,
        difficulty=difficulty,
        attempts={},
    )
    image_path = render_hand_image(question.hand)
    message = Message(ms.image(Request(Path(image_path).as_uri()).local_content))
    message += (
        f"{question.hand_code}\n"
        "请回答听牌编码，例如：58p、5p8p、19m19s1234567z；如果判断未听牌，请回答：未听牌。\n"
        f"本题可多人作答，每人最多猜 {TENPAI_MAX_GUESSES} 次；猜错不会公布答案。"
    )
    await GuessTenpaiMatcher.send(ms.at(event.user_id) + message)


@GuessTenpaiAnswerMatcher.handle()
async def _(event: MessageEvent):
    answer = event.message.extract_plain_text().strip()
    game_key = _tenpai_session_key(event)
    game = active_tenpai_games.get(game_key)
    if game is None or not _is_tenpai_answer_candidate(answer):
        return

    current_attempts = game.attempts.get(event.user_id, 0)
    if current_attempts >= TENPAI_MAX_GUESSES:
        await GuessTenpaiAnswerMatcher.finish(ms.at(event.user_id) + " 你已经用完本题的 5 次机会啦。")

    game.attempts[event.user_id] = current_attempts + 1
    wait_code = tiles_to_code(game.waits) if game.waits else "未听牌"
    if is_correct_answer(answer, game.waits):
        active_tenpai_games.pop(game_key, None)
        await GuessTenpaiAnswerMatcher.finish(ms.at(event.user_id) + f" 回答正确！听牌：{wait_code}")

    remaining = TENPAI_MAX_GUESSES - game.attempts[event.user_id]
    if remaining <= 0:
        active_tenpai_games.pop(game_key, None)
        await GuessTenpaiAnswerMatcher.finish(ms.at(event.user_id) + f" 回答错误，5 次机会已用完。正确答案：{wait_code}")
    await GuessTenpaiAnswerMatcher.finish(ms.at(event.user_id) + f" 回答错误或不完整，还可以再猜 {remaining} 次。")
