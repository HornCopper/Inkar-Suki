from .chutian import *
from .yuncong import *
from .zhue import *

cts = on_command("jx3_chutian", aliases={"楚天社"}, priority=5)

@cts.handle()
async def _(event: GroupMessageEvent):
    image = await getChutianImg()
    await cts.finish(ms.image(image))

ycs = on_command("jx3_yuncong", priority=5, aliases={"云从社"})

@ycs.handle()
async def _(event: GroupMessageEvent):
    return # 正在施工

zhue_ = on_command("jx3_zhue", aliases={"诛恶"}, priority=5)

@zhue_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    server = server_mapping(args.extract_plain_text(), str(event.group_id))
    if server == None:
        await zhue_.finish(PROMPT_ServerNotExist)
    else:
        image = await getZhueRecord(server)
        await zhue_.finish(ms.image(image))