import asyncio
from asyncio import TimerHandle
from typing import Any, Dict
from nonebot import on_regex, on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RegexDict
from nonebot.rule import to_me
from nonebot.utils import run_sync
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent

from .data_source import GuessResult, Handle
from .utils import random_idiom

games: Dict[str, Handle] = {}
timers: Dict[str, TimerHandle] = {}


def game_is_running(user_id: str) -> bool:
    return user_id in games


def game_not_running(user_id: str) -> bool:
    return user_id not in games


handle = on_command("猜成语", rule=to_me() & game_not_running, priority=13, block=True)
handle_hint = on_command("提示", rule=game_is_running, priority=13, block=True)
handle_stop = on_command("结束", aliases={"结束游戏", "结束猜成语"}, rule=game_is_running, priority=13, block=True)
handle_idiom = on_regex(r"^(?P<idiom>[\u4e00-\u9fa5]{4})$", rule=game_is_running, priority=14, block=True)


def stop_game(user_id: str):
    if timer := timers.pop(user_id, None):
        timer.cancel()
    games.pop(user_id, None)


async def stop_game_timeout(bot: Bot, user_id: str):
    game = games.get(user_id, None)
    stop_game(user_id)
    if game:
        msg = "猜成语超时，游戏结束。"
        if len(game.guessed_idiom) >= 1:
            msg += f"\n{game.result}"
        await bot.send_private_msg(user_id=int(user_id), message=msg)


def set_timeout(bot: Bot, user_id: str, timeout: float = 300):
    if timer := timers.get(user_id, None):
        timer.cancel()
    loop = asyncio.get_running_loop()
    timer = loop.call_later(
        timeout, lambda: asyncio.ensure_future(stop_game_timeout(bot, user_id))
    )
    timers[user_id] = timer


@handle.handle()
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    user_id = str(event.user_id)
    is_strict = "--strict" in args.extract_plain_text().split()

    idiom, explanation = random_idiom()
    game = Handle(idiom, explanation, strict=is_strict)

    games[user_id] = game
    set_timeout(bot, user_id)

    msg = (
        f"你有{game.times}次机会猜一个四字成语，"
        + ("发送有效成语以参与游戏。" if is_strict else "发送任意四字词语以参与游戏。")
    ) + MessageSegment.image(await run_sync(game.draw)())
    await matcher.send(msg)


@handle_hint.handle()
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent):
    user_id = str(event.user_id)
    game = games[user_id]
    set_timeout(bot, user_id)

    await matcher.send(MessageSegment.image(await run_sync(game.draw_hint)()))


@handle_stop.handle()
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent):
    user_id = str(event.user_id)
    game = games[user_id]
    stop_game(user_id)

    msg = "游戏已结束"
    if len(game.guessed_idiom) >= 1:
        msg += f"\n{game.result}"
    await matcher.send(msg)


@handle_idiom.handle()
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent, matched: Dict[str, Any] = RegexDict()):
    user_id = str(event.user_id)
    game = games[user_id]
    set_timeout(bot, user_id)

    idiom = str(matched["idiom"])
    result = game.guess(idiom)

    if result in [GuessResult.WIN, GuessResult.LOSS]:
        stop_game(user_id)
        msg = (
            (
                "恭喜你猜出了成语！"
                if result == GuessResult.WIN
                else "很遗憾，没有人猜出来呢"
            )
            + f"\n{game.result}"
        ) + MessageSegment.image(await run_sync(game.draw)())
        await matcher.send(msg)

    elif result == GuessResult.DUPLICATE:
        await matcher.send("你已经猜过这个成语了呢")

    elif result == GuessResult.ILLEGAL:
        await matcher.send(f"你确定“{idiom}”是个成语吗？")

    else:
        await matcher.send(MessageSegment.image(await run_sync(game.draw)()))