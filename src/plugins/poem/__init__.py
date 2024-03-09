from src.plugins.sign import Sign

from .api import *

question = ""

rdp = on_command("randomPoem", aliases={"对诗"}, priority=5)

@rdp.handle()
async def _(state: T_State, event: Event):
    data = await getRandomPoem()
    content = data[0]
    title = data[1]
    author = data[2]
    contents = content.split("，")
    rdPart = random.randint(0, len(contents) - 1)
    guess = contents[rdPart]
    if guess[-1] in ["？", "！", "。"]:
        guess = guess[0:-1]
    blank = content.replace(guess, "__________")
    state["author"] = author
    state["title"] = title
    state["answer"] = guess
    global question
    question = f"请听题！\n{blank}"

@rdp.got("answer", prompt=question)
async def __(event: Event, state: T_State, answer: Message = Arg()):
    ans = answer.extract_plain_text()
    if ans == state["guess"]:
        Sign.add(str(event.user_id), 50)
        author = state["author"]
        title = state["title"]
        await rdp.finish(f"答对啦！\n这首诗是 {author} 的《{title}》。\n您获得了50枚金币。")