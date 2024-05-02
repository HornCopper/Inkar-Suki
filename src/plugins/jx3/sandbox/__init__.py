from .api import *

sandbox = on_command("jx3_sandbox", aliases={"沙盘"}, force_whitespace=True, priority=5)

@sandbox.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取服务器沙盘：

    Example：-沙盘 幽月轮
    """
    server = args.extract_plain_text()
    server = server_mapping(server, str(event.group_id))
    data = await sandbox_(server)
    if type(data) == type([]):
        await sandbox.finish(data[0])
    else:
        data = await get_content(data)
        await sandbox.finish(ms.image(data))