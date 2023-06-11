from src.tools.dep.bot import *
from .api import *

demon = on_command("jx3_demon", aliases={"金价"}, priority=5)
@demon.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取各服金价：

    Example：-金价 幽月轮
    '''
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text()
    if arg == "":
        if group_server == False:
            await demon.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
    else:
        server = arg
    data = await demon_(server)
    if type(data) == type([]):
        await demon.finish(data[0])
    else:
        await demon.finish(ms.image(data))