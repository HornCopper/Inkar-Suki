from .api import *

cmd_jx3_server = on_command("jx3_server", aliases = {"服务器", "开服"}, priority = 5)

@cmd_jx3_server.handle()
async def jx3_server(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取服务器开服状态：

    Example：-服务器 幽月轮
    Example：-开服 幽月轮 
    """
    server = args.extract_plain_text()
    srv = server_mapping(server, str(event.group_id))
    if srv == None:
        await cmd_jx3_server.finish(PROMPT_ServerNotExist)
    msg = await server_status(srv)
    await cmd_jx3_server.finish()