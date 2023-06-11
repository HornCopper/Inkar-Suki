from src.tools.dep.bot import *
from .api import *

sandbox = on_command("jx3_sandbox", aliases={"沙盘"}, priority=5)
@sandbox.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取服务器沙盘：

    Example：-沙盘 幽月轮
    '''
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text()
    if arg == "":
        if group_server == False:
            await sandbox.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
    else:
        server = arg
    data = await sandbox_(server)
    if type(data) == type([]):
        await sandbox.finish(data[0])
    else:
        await sandbox.finish(ms.image(data))
