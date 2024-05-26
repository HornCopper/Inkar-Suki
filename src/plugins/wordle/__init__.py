import asyncio
from asyncio import TimerHandle
from typing import Any, Dict

from nonebot import on_regex, require
from nonebot.matcher import Matcher
from nonebot.params import RegexDict
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.rule import to_me
from nonebot.utils import run_sync
from typing_extensions import Annotated

require("nonebot_plugin_alconna")
require("nonebot_plugin_session")

from nonebot_plugin_alconna import (
    Alconna,
    AlconnaQuery,
    Image,
    Option,
    Query,
    Text,
    UniMessage,
    on_alconna,
    store_true,
)
from nonebot_plugin_session import SessionId, SessionIdType

from .config import Config, handle_config
from .data_source import GuessResult, Handle
from .utils import random_idiom

__plugin_meta__ = PluginMetadata(
    name="猜成语",
    description="汉字Wordle 猜成语",
    usage=(
        "@我 + “猜成语”开始游戏；\n"
        "你有十次的机会猜一个四字词语；\n"
        "每次猜测后，汉字与拼音的颜色将会标识其与正确答案的区别；\n"
        "青色 表示其出现在答案中且在正确的位置；\n"
        "橙色 表示其出现在答案中但不在正确的位置；\n"
        "每个格子的 汉字、声母、韵母、声调 都会独立进行颜色的指示。\n"
        "当四个格子都为青色时，你便赢得了游戏！\n"
        "可发送“结束”结束游戏；可发送“提示”查看提示。\n"
        "使用 --strict 选项开启非默认的成语检查，即猜测的短语必须是成语，\n"
        "如：@我 猜成语 --strict"
    ),
    type="application",
    homepage="https://github.com/noneplugin/nonebot-plugin-handle",
    config=Config,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_session"
    ),
    extra={
        "example": "@小Q 猜成语",
    },
)


games: Dict[str, Handle] = {}
timers: Dict[str, TimerHandle] = {}

UserId = Annotated[str, SessionId(SessionIdType.GROUP)]


def game_is_running(user_id: UserId) -> bool:
    return user_id in games


def game_not_running(user_id: UserId) -> bool:
    return user_id not in games


handle = on_alconna(
    Alconna("handle", Option("-s|--strict", default=False, action=store_true)),
    aliases=("猜成语",),
    rule=to_me() & game_not_running,
    use_cmd_start=True,
    block=True,
    priority=13,
)
handle_hint = on_alconna(
    "提示",
    rule=game_is_running,
    use_cmd_start=True,
    block=True,
    priority=13,
)
handle_stop = on_alconna(
    "结束",
    aliases=("结束游戏", "结束猜成语"),
    rule=game_is_running,
    use_cmd_start=True,
    block=True,
    priority=13,
)
handle_idiom = on_regex(
    r"^(?P<idiom>[\u4e00-\u9fa5]{4})$",
    rule=game_is_running,
    block=True,
    priority=14,
)


def stop_game(user_id: str):
    if timer := timers.pop(user_id, None):
        timer.cancel()
    games.pop(user_id, None)


async def stop_game_timeout(matcher: Matcher, user_id: str):
    game = games.get(user_id, None)
    stop_game(user_id)
    if game:
        msg = "猜成语超时，游戏结束。"
        if len(game.guessed_idiom) >= 1:
            msg += f"\n{game.result}"
        await matcher.finish(msg)


def set_timeout(matcher: Matcher, user_id: str, timeout: float = 300):
    if timer := timers.get(user_id, None):
        timer.cancel()
    loop = asyncio.get_running_loop()
    timer = loop.call_later(
        timeout, lambda: asyncio.ensure_future(stop_game_timeout(matcher, user_id))
    )
    timers[user_id] = timer


@handle.handle()
async def _(
    matcher: Matcher,
    user_id: UserId,
    strict: Query[bool] = AlconnaQuery("strict.value", False),
):
    is_strict = handle_config.handle_strict_mode or strict.result
    idiom, explanation = random_idiom()
    game = Handle(idiom, explanation, strict=is_strict)

    games[user_id] = game
    set_timeout(matcher, user_id)

    msg = Text(
        f"你有{game.times}次机会猜一个四字成语，"
        + ("发送有效成语以参与游戏。" if is_strict else "发送任意四字词语以参与游戏。")
    ) + Image(raw=await run_sync(game.draw)())
    await msg.send()


@handle_hint.handle()
async def _(matcher: Matcher, user_id: UserId):
    game = games[user_id]
    set_timeout(matcher, user_id)

    await UniMessage.image(raw=await run_sync(game.draw_hint)()).send()


@handle_stop.handle()
async def _(matcher: Matcher, user_id: UserId):
    game = games[user_id]
    stop_game(user_id)

    msg = "游戏已结束"
    if len(game.guessed_idiom) >= 1:
        msg += f"\n{game.result}"
    await matcher.finish(msg)


@handle_idiom.handle()
async def _(matcher: Matcher, user_id: UserId, matched: Dict[str, Any] = RegexDict()):
    game = games[user_id]
    set_timeout(matcher, user_id)

    idiom = str(matched["idiom"])
    result = game.guess(idiom)

    if result in [GuessResult.WIN, GuessResult.LOSS]:
        stop_game(user_id)
        msg = Text(
            (
                "恭喜你猜出了成语！"
                if result == GuessResult.WIN
                else "很遗憾，没有人猜出来呢"
            )
            + f"\n{game.result}"
        ) + Image(raw=await run_sync(game.draw)())
        await msg.send()

    elif result == GuessResult.DUPLICATE:
        await matcher.finish("你已经猜过这个成语了呢")

    elif result == GuessResult.ILLEGAL:
        await matcher.finish(f"你确定“{idiom}”是个成语吗？")

    else:
        await UniMessage.image(raw=await run_sync(game.draw)()).send()
