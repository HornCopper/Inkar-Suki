from .chutian import *
from .yuncong import *
from .zhue import *

cts = on_command("jx3_chutian", aliases={"楚天社"}, force_whitespace=True, priority=5)

@cts.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    image = await getChutianImg()
    image = get_content_local(image)
    await cts.finish(ms.image(image))

ycs = on_command("jx3_yuncong", aliases={"云从社"}, force_whitespace=True, priority=5)

@ycs.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    image = await getYuncongImg()
    image = get_content_local(image)
    await ycs.finish(ms.image(image))

zhue_ = on_command("jx3_zhue", aliases={"诛恶"}, force_whitespace=True, priority=5)

@zhue_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    server = server_mapping(args.extract_plain_text(), str(event.group_id))
    if server == None:
        await zhue_.finish(PROMPT_ServerNotExist)
    else:
        image = await getZhueRecord(server)
        image = get_content_local(image)
        await zhue_.finish(ms.image(image))