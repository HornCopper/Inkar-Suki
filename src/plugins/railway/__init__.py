from .crt import *

cq = on_command("crt", priority=5)

@cq.handle()
async def _(event: Event, args: Message = CommandArg()):
    arg = args.extract_plain_text()
    if len(arg.split(" ")) != 2:
        await cq.finish("请给出起始站点和终止站点！")
    else:
        start = arg[0]
        end = arg[1]
        image = await cq_crt(start, end)
        image = get_content_local(image)
        await cq.finish(ms.image(image))