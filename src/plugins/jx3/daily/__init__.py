from .api import *

jx3_cmd_daily = on_command("jx3_daily", aliases={"日常", "周常"}, priority=5)


@jx3_cmd_daily.handle()
async def jx3_daily(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    查询日常。

    Notice：每个服务器的日常相同，仅美人图有可能存在不同。

    Example：-日常
    Example：-周常
    Example：-日常 幽月轮
    """
    img = await daily_(args.extract_plain_text(), group_id=event.group_id)
    if isinstance(img, list):
        return await jx3_cmd_daily.finish(img[0])
    return await jx3_cmd_daily.finish(ms.image(img))
