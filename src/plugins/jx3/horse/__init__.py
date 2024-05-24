from .api import *

jx3_cmd_horse = on_command("jx3_horse_v1", aliases={"抓马v1", "马场v1"}, force_whitespace=True, priority=5)

@jx3_cmd_horse.handle()
async def jx3_horse_v1(event: GroupMessageEvent, args: Message = CommandArg()):
    server = args.extract_plain_text()
    msg = await get_horse_reporter(server, group_id=event.group_id)
    await jx3_cmd_horse.finish(msg)

jx3_cmd_horse_v2 = on_command("jx3_horse_v2", aliases={"抓马", "马场"}, force_whitespace=True, priority=5)

@jx3_cmd_horse_v2.handle()
async def jx3_horse_v2(event: GroupMessageEvent, args: Message = CommandArg()):
    server = args.extract_plain_text()
    msg = await get_horse_next_spawn(server, str(event.group_id))
    await jx3_cmd_horse_v2.finish(msg)