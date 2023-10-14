from .detail import *

zone_detail = on_command("jx3_zone_detail", aliases={"副本总览"}, priority=5)

@zone_detail.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await zone_detail.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server == False:
            await zone_detail.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await generate_zd_image(server, id)
    if type(data) == type([]):
        await zone_detail.finish(data[0])
    else:
        await zone_detail.finish(ms.image(data))
