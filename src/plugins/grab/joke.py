from src.tools.basic import *

api = "https://api.qicaiyun.top/joke/api.php"

async def get_joke():
    data = await get_url(api)
    msg = "、".join(data.split("、")[1:])
    return msg

rdcoldjoke = on_command("冷笑话", priority=5, force_whitespace=True)

@rdcoldjoke.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    msg = await get_joke()
    await rdcoldjoke.finish(msg)