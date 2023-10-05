from .api import *

firework = on_command("jx3_firework_v2", aliases={"烟花v2"}, priority=5)
@firework.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        return await firework.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await get_firework_image(server, id, group_id=event.group_id)
    if type(data) == type([]):
        return await firework.finish(data[0])
    else:
        return await firework.finish(ms.image(data))