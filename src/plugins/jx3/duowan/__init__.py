from .api import *

tz = on_command("jx3_tongzhan", aliases={"统战", "统战YY", "统战yy"})

@tz.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    server = server_mapping(args.extract_plain_text(), str(event.group_id))
    if server == None:
        await tz.finish(PROMPT_ServerNotExist)
    else:
        image = await getTongzhan(server)
        image = get_content_local(image)
        await tz.finish(ms.image(image))