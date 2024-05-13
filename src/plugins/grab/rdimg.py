from src.tools.basic import *

rdci = on_command("随机猫图", priority=5)

rddi = on_command("随机狗图", priority=5)

@rdci.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    data = await get_api("https://api.thecatapi.com/v1/images/search?size=full")
    image = await get_content(data[0]["url"])
    await rdci.finish(ms.image(image))

@rddi.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    data = await get_api("https://api.thedogapi.com/v1/images/search?size=full")
    image = await get_content(data[0]["url"])
    await rddi.finish(ms.image(image))