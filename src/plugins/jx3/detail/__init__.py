from src.plugins.sign import Sign

from .detail import *

zone_detail = on_command("jx3_zone_detail", aliases={"副本总览"}, force_whitespace=True, priority=5)

@zone_detail.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await zone_detail.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server is False:
            await zone_detail.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await generate_zd_image(server, id)
    if isinstance(data, list):
        await zone_detail.finish(data[0])
    else:
        data = get_content_local(data)
        await zone_detail.finish(ms.image(data))

global_dungeon_lookup = on_command("jx3_global_dungeon", aliases={"副本分览"}, force_whitespace=True, priority=5)

@global_dungeon_lookup.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    coin = Sign.get_coin(str(event.user_id))
    if coin < 500:
        await global_dungeon_lookup.finish("副本分览正在内测，需要500金币才能使用哦！")
    else:
        Sign.reduce(str(event.user_id), 500)
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await global_dungeon_lookup.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await get_all_dungeon_image(server, id, str(event.group_id))
    if isinstance(data, list):
        await global_dungeon_lookup.finish(data[0])
    else:
        data = get_content_local(data)
        await global_dungeon_lookup.finish(ms.image(data))