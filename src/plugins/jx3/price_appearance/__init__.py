from .api import *

item_price = on_command("jx3_price", aliases={"物价"}, priority=5)

@item_price.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取外观物价：

    Example：-物价 山神盒子
    Example：-物价 大橙武券
    """
    arg = args.extract_plain_text()
    if arg == "":
        await item_price.finish("缺少物品名称，没办法找哦~")
    data = await item_(arg)
    if type(data) == type([]):
        await item_price.finish(data[0])
    else:
        await item_price.finish(ms.image(data))
