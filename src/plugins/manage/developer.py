from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from src.utils.permission import check_permission
from src.utils.generate import generate

ScreenShotMatcher = on_command("screenshot", priority=5, force_whitespace=True)

@ScreenShotMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    url = args.extract_plain_text()
    if not url.startswith("http"):
        return
    if not check_permission(event.user_id, 8):
        return
    try:
        image = await generate(url, full_screen=True, viewport={"height": 1080, "width": 1920}, segment=True)
    except:
        await ScreenShotMatcher.finish("Screenshot Failed!")
    await ScreenShotMatcher.finish(image)