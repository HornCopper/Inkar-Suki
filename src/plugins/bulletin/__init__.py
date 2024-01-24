from .api import *

bulletin_glad = on_command("喜报", priority=5)

@bulletin_glad.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg == "":
        await bulletin_glad.finish("唔……你还没有输入喜报的内容呢！")
    elif len(msg) > 20:
        await bulletin_glad.finish("字数请控制在20字以内！")
    else:
        img = await get_bulletinG(msg)
        await bulletin_glad.finish(ms.image(img))
    