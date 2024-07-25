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
    if isinstance(data, list):
        await sandbox.finish(data[0])
    else:
        data = await get_content(data)
        await sandbox.finish(ms.image(data))


sandbox_v2 = on_command("jx3_sandbox_v2", aliases={"沙盘v2"}, force_whitespace=True, priority=5)

@sandbox_v2.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取服务器沙盘：
    Example：-沙盘v2 幽月轮
    """
    server = args.extract_plain_text()
    server = server_mapping(server, str(event.group_id))
    data = await sandbox_v2_(server)
    if isinstance(data, list):
        await sandbox_v2.finish(data[0])
    else:
        data = get_content_local(data)
        await sandbox_v2.finish(ms.image(data))