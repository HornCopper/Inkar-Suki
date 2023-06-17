from src.tools.dep.bot import *
from .api import *
     
daily = on_command("jx3_daily", aliases={"日常","周常"}, priority=5)
@daily.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    查询日常。

    Notice：每个服务器的日常相同，仅美人图有可能存在不同。

    Example：-日常
    Example：-周常
    Example：-日常 幽月轮
    '''
    img = await daily_(args.extract_plain_text(),group_id=event.group_id)
    await daily.finish(ms.image(img))