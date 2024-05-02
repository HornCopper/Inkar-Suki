from .crt import *

cq = on_command("crt", force_whitespace=True, priority=5)

@cq.handle()
async def _(event: Event, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await cq.finish("请给出起始站点和终止站点！")
    else:
        start = arg[0]
        end = arg[1]
        image = await cq_crt(start, end)
        if type(image) == type([]):
            await cq.finish(image[0])
        image = get_content_local(image)
        await cq.finish(ms.image(image))