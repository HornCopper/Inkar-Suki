from .api import *

trade = on_command("交易行", priority=5)


@trade.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        return await trade.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    img = await getImg(server, id, str(event.group_id))
    if type(img) == type([]):
        await trade.finish(img[0])
    else:
        await trade.finish(ms.image(img))