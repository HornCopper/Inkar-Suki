from .api import *

sandbox = on_command("jx3_sandbox", aliases = {"沙盘"}, priority = 5)


@sandbox.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取服务器沙盘：

    Example：-沙盘 幽月轮
    '''
    server = args.extract_plain_text()
    data = await sandbox_(server, group_id = event.group_id)
    if type(data) == type([]):
        await sandbox.finish(data[0])
    else:
        await sandbox.finish(ms.image(data))
