from .api import *

calendar = on_command("jx3_calendar", aliases={"活动日历", "剑三日历"}, force_whitespace=True, priority=5)

@calendar.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    image = await getCalendar()
    image = get_content_local(image)
    await calendar.finish(ms.image(image))