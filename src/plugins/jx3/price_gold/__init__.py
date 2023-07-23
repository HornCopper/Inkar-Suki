from .api import *

demon = on_command("jx3_demon", aliases = {"金价"}, priority = 5)

@demon.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取各服金价：

    Example：-金价 幽月轮
    """
    server = args.extract_plain_text()
    data = await demon_(server, group_id = event.group_id)
    if type(data) == type([]):
        await demon.finish(data[0])
    else:
        await demon.finish(ms.image(data))
