from nonebot.adapters.onebot.v11 import PokeNotifyEvent, MessageSegment as ms
from nonebot import on_notice

poke_me = on_notice(priority=5)

@poke_me.handle()
async def _(event: PokeNotifyEvent):
    if event.group_id == None:
        return
    else:
        await poke_me.finish("音卡在呢！找音卡有什么事吗！(^ω^)" + ms.image("https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/emoji.jpg"))