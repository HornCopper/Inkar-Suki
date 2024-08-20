from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment as ms

from src.tools.basic.msg import PROMPT
from src.tools.file import get_content_local

from .leader import *
from .api import *

arena_re = on_command("jx3_arena_record", aliases={"战绩"}, force_whitespace=True, priority=5)

@arena_re.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await arena_re.finish(PROMPT.ArgumentCountInvalid)
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await arena_record(server, id, group_id=str(event.group_id))
    if isinstance(data, list):
        await arena_re.finish(data[0])
    else:
        data = get_content_local(data)
        await arena_re.finish(ms.image(data))
    # arg = args.extract_plain_text().split(" ")
    # if len(arg) not in [1, 2, 3]:
    #     # 1 -> 战绩 xxx
    #     # 2 -> 战绩 srv xx / 战绩 xx 22(33or55)
    #     # 3 -> 战绩 srv xx 22(33or55)
    #     await arena_re.finish(PROMPT.ArgumentCountInvalid)
    # if len(arg) == 1:
    #     server = None
    #     name = arg[0]
    # elif len(arg) == 2:
    #     if arg[-1] not in ["22", "33", "55"]: 
    #         server = arg[0]
    #         name = arg[1]
    #     else:
    #         server = None
    #         name = arg[0]
    #         mode = arg[1]
    # else:
    #     server = arg[0]
    #     name = arg[1]
    #     mode = arg[2]
    # data = await arena_record(server=server, name=name, group_id=event.group_id)
    # if isinstance(data, list):
    #     await arena_re.finish(data[0])
    # else:
    #     data = await get_content(data)
    #     await arena_re.finish(ms.image(data))

arena_ra = on_command("jx3_arena_rank", aliases={"排行"}, force_whitespace=True, priority=5)

@arena_ra.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    # arg = args.extract_plain_text().split(" ")
    # if arg[0] not in ["22", "33", "55"]:
    #     await arena_ra.finish("唔……名剑模式只接受22、33、55！")
    # data = await arena_rank(mode=arg[0])
    # if isinstance(data, list):
    #     await arena_ra.finish(data[0])
    # else:
    #     data = await get_content(data)
    #     await arena_ra.finish(ms.image(data))

arena_s = on_command("jx3_arena_stastic", aliases={"统计"}, force_whitespace=True, priority=5)

@arena_s.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    # arg = args.extract_plain_text().split(" ")
    # if arg[0] not in ["22", "33", "55"]:
    #     await arena_s.finish("唔……名剑模式只接受22、33、55！")
    # data = await arena_stastic(mode=arg[0])
    # if isinstance(data, list):
    #     await arena_s.finish(data[0])
    # else:
    #     data = await get_content(data)
    #     await arena_s.finish(ms.image(data))

lks = on_command("jx3_lks", aliases={"烂柯山"}, force_whitespace=True, priority=5)

@lks.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    # img = await getLKSImage()
    # data = get_content_local(img)
    # await lks.finish(ms.image(data))