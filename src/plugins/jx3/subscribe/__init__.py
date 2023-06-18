from src.tools.dep.bot import *
from src.tools.file import *
from .api import *

subscribe = on_command("jx3_subscribe", aliases={"订阅"}, priority=5)
@subscribe.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    订阅内容，可选择订阅的内容：

    目前支持：玄晶、新闻、开服、更新。

    Example：-订阅 玄晶

    Notice：一次只可订阅一个。
    '''
    path = DATA + "/" + str(event.group_id) + "/subscribe.json"
    now = json.loads(read(path))
    obj = args.extract_plain_text()
    if obj not in ["玄晶","公告","开服","更新","818"]:
        await subscribe.finish("请不要订阅一些很奇怪的东西，我可是无法理解的哦~")
    if obj in now:
        await subscribe.finish("已经订阅了哦，请不要重复订阅~")
    now.append(obj)
    write(path, json.dumps(now, ensure_ascii=False))
    await subscribe.finish(f"已开启本群的{obj}订阅！当收到事件时会自动推送，如需取消推送，请发送：-退订 {obj}")

unsubscribe = on_command("jx3_unsubscribe", aliases={"退订"}, priority=5)
@unsubscribe.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    退订某内容，可选择：

    同上。

    Example：-退订 开服
    '''
    path = DATA + "/" + str(event.group_id) + "/subscribe.json"
    now = json.loads(read(path))
    obj = args.extract_plain_text()
    if obj not in ["玄晶","公告","开服","更新","818"]:
        await subscribe.finish("请不要取消订阅一些很奇怪的东西，我可是无法理解的哦~")
    if obj not in now:
        await subscribe.finish("尚未订阅，无法取消订阅哦~")
    now.remove(obj)
    write(path, json.dumps(now, ensure_ascii=False))
    await subscribe.finish(f"已关闭本群的{obj}订阅！如需再次开启，请发送：\n-订阅 {obj}")
