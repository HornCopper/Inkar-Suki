from src.plugins.sign import Sign

from .api import *
from .v4 import *

addritube_v1 = on_command("jx3_addritube", aliases={"属性v1", "查装v1"}, force_whitespace=True, priority=5)

@addritube_v1.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    查询某玩家的装备：

    Example：-属性v1 幽月轮 哭包猫@唯我独尊
    Example：-查装v1 幽月轮 哭包猫@唯我独尊
    """
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await addritube_v1.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await addritube_(server, id, group_id=event.group_id)
    if type(data) == type([]):
        await addritube_v1.finish(data[0])
    else:
        data = await get_content(data)
        await addritube_v1.finish(ms.image(data))

addritube_v2 = on_command("jx3_addritube_v2", aliases={"属性", "查装", "属性v2", "查装v2"}, force_whitespace=True, priority=5)

@addritube_v2.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    查询某玩家的装备：

    Example：-属性 幽月轮 哭包猫@唯我独尊
    Example：-查装 幽月轮 哭包猫@唯我独尊
    """
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await addritube_v2.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await get_attr_main(server, id, str(event.group_id))
    if type(data) == type([]):
        await addritube_v2.finish(data[0])
    else:
        data = get_content_local(data)
        await addritube_v2.finish(ms.image(data))

addritube_v4 = on_command("jx3_addritube_v4", aliases={"属性v4", "查装v4"}, force_whitespace=True, priority=5)

@addritube_v4.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    查询某玩家的装备：

    Example：-属性v4 幽月轮 哭包猫@唯我独尊
    Example：-查装v4 幽月轮 哭包猫@唯我独尊
    """
    if args.extract_plain_text() == "":
        return
    coin = Sign.get_coin(str(event.user_id))
    if coin < 50:
        await addritube_v4.finish("属性v4正在内测，需要50金币才能使用哦！")
    else:
        Sign.reduce(str(event.user_id), 50)
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await addritube_v4.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await get_attrs_v4(server, id, str(event.group_id))
    if type(data) == type([]):
        await addritube_v4.finish(data[0])
    else:
        data = get_content_local(data)
        await addritube_v4.finish(ms.image(data))

roleInfo = on_command("jx3_player", aliases={"玩家信息"}, force_whitespace=True, priority=5)

@roleInfo.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取玩家信息：

    Example：-玩家信息 幽月轮 哭包猫@唯我独尊
    """
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await roleInfo.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    msg = await roleInfo_(server=server, player=id, group_id=str(event.group_id))
    await roleInfo.finish(msg)