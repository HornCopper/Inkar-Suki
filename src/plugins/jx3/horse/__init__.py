from .api import *

jx3_cmd_horse = on_command("jx3_horse_v1", aliases={"抓马", "马场"}, force_whitespace=True, priority=5)


@jx3_cmd_horse.handle()
async def jx3_horse_v1(event: GroupMessageEvent, args: Message = CommandArg()):
    server = args.extract_plain_text()
    msg = await get_horse_reporter(server, group_id=event.group_id)
    await jx3_cmd_horse.finish(msg)
