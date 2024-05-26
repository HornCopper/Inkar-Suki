from .api import *

bulletin_glad = on_command("喜报", force_whitespace=True, priority=5)

@bulletin_glad.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    msg = args.extract_plain_text()
    if msg == "":
        await bulletin_glad.finish("唔……你还没有输入喜报的内容呢！")
    elif len(msg) > 20:
        await bulletin_glad.finish("字数请控制在20字以内！")
    else:
        img = await get_bulletinG(msg, "G")
        await bulletin_glad.finish(ms.image(img))

bulletin_sad = on_command("悲报", force_whitespace=True, priority=5)

@bulletin_sad.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    msg = args.extract_plain_text()
    if msg == "":
        await bulletin_sad.finish("唔……你还没有输入悲报的内容呢！")
    elif len(msg) > 20:
        await bulletin_sad.finish("字数请控制在20字以内！")
    else:
        img = await get_bulletinG(msg, "S")
        await bulletin_sad.finish(ms.image(img))


self_ban = on_command("禁言我", force_whitespace=True, priority=5)

@self_ban.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    num = random.randint(1, 720)
    await bot.call_api("set_group_ban", user_id=event.user_id, group_id=event.group_id, duration=num*60)
    await self_ban.finish(f"自助禁言成功！音卡送您{num}分钟的红茶~")
