from .leader import *
from .api import *

arena = on_command("jx3_arena", aliases={"名剑"}, force_whitespace=True, priority=5)


@arena.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [2, 3, 4]:
        await arena.finish(PROMPT_ArgumentCountInvalid)
    if arg[0] == "战绩":
        if len(arg) not in [2, 3, 4]:
            await arena.finish(PROMPT_ArgumentCountInvalid)
        mode = "22"
        if len(arg) == 2:
            server = None
            name = arg[1]
        elif len(arg) == 3:
            server = arg[1]
            name = arg[2]
        else:
            server = arg[1]
            name = arg[2]
            mode = arg[3]
        data = await arena_(object="战绩", server=server, name=name, group_id=event.group_id, mode=mode)
        if type(data) == type([]):
            await arena.finish(data[0])
        else:
            data = await get_content(data)
            await arena.finish(ms.image(data))
    elif arg[0] == "排行":
        if len(arg) != 2:
            await arena.finish(PROMPT_ArgumentCountInvalid)
        data = await arena_(object="排行", mode=arg[1], group_id=event.group_id)
        if type(data) == type([]):
            await arena.finish(data[0])
        else:
            data = await get_content(data)
            await arena.finish(ms.image(data))
    elif arg[0] == "统计":
        if len(arg) != 2:
            await arena.finish(PROMPT_ArgumentCountInvalid)
        data = await arena_(object="统计", mode=arg[1], group_id=event.group_id)
        if type(data) == type([]):
            await arena.finish(data[0])
        else:
            data = await get_content(data)
            await arena.finish(ms.image(data))

lks = on_command("jx3_lks", aliases={"烂柯山"}, force_whitespace=True, priority=5)

@lks.handle()
async def _(event: GroupMessageEvent):
    img = await getLKSImage()
    data = get_content_local(img)
    await lks.finish(ms.image(data))