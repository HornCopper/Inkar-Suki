import sys
import nonebot

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from utils import checknumber

from .gettor import get_tieba

tieba = on_command("tieba", aliases={"贴吧"}, priority=5)
@tieba.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    tid = args.extract_plain_text()
    if checknumber(tid) == False:
        await tieba.finish("请给出纯数字的帖子ID哦~")
    msg = await get_tieba(int(tid))
    await tieba.finish(msg)
    