from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg, Received
from nonebot.typing import T_State

from src.accounts.manage import AccountManage

from .api import get_poem

import random

PoemMatcher = on_command("randomPoem", aliases={"对诗"}, force_whitespace=True, priority=5)

@PoemMatcher.handle()
async def _(state: T_State, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    data = await get_poem()
    content = data[0]
    title = data[1]
    author = data[2]
    contents = content.split("，")
    if len(contents) == 1:
        contents = content.split("。")
    rdPart = random.randint(0, len(contents) - 1)
    guess = contents[rdPart]
    if guess[-1] in ["？", "！", "。"]:
        guess = guess[0:-1]
    blank = content.replace(guess, "__________")
    state["raw"] = content
    state["author"] = author
    state["title"] = title
    state["answer"] = guess
    question = f"请听题！\n{blank}"
    await PoemMatcher.send(question)
    return


@PoemMatcher.receive("answer")
async def __(state: T_State, event: MessageEvent = Received("answer")):
    ans = str(event.message)
    if ans == state["answer"]:
        AccountManage(event.user_id).add_coin(5000)
        author = state["author"]
        title = state["title"]
        await PoemMatcher.finish(f"答对啦！\n这句诗来自 {author} 的《{title}》。\n您获得了 5000 枚金币。")
    else:
        AccountManage(event.user_id).reduce_coin(6200)
        right = state["raw"]
        author = state["author"]
        title = state["title"]
        await PoemMatcher.finish(f"唔……答错了！\n这句诗来自 {author} 的《{title}》。\n很可惜，您失去了 6200 枚金币。\n正确答案为：{right}")