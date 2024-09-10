from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.tools.config import Config
from src.tools.utils.num import check_number
from src.tools.utils.file import get_content_local

from .api import *

cheater = on_command("jx3_cheater", aliases={"查人", "骗子"}, force_whitespace=True, priority=5)

@cheater.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "" or not Config.jx3.api.enable:
        return
    uin = args.extract_plain_text()
    if not check_number(uin):
        await cheater.finish("唔……查人请给出纯数字的QQ号！")
    if int(uin) > 9999999999 or int(uin) < 100000:
        await cheater.finish("唔……该QQ号无效！")
    data = await getAwesomeRecord(uin)
    if not data:
        await cheater.finish("查询完毕，没有发现贴吧有Ta的记录哦~")
    else:
        await cheater.send("查询完毕，已发现贴吧记录，正在生成图片……")
        data = get_content_local(data)
        await cheater.finish(ms.image(data))