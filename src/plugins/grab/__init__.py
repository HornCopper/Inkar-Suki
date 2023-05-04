import sys
import nonebot

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from src.tools.utils import checknumber

from .gettor import get_tieba
from .gettor import what2eat

tieba = on_command("-tieba", aliases={"-贴吧"}, priority=5)
@tieba.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    贴吧内容查询，具体实现参考`gettor.py`的`get_tieba`函数。
    '''
    tid = args.extract_plain_text()
    if checknumber(tid) == False:
        await tieba.finish("请给出纯数字的帖子ID哦~")
    msg = await get_tieba(int(tid))
    await tieba.finish(msg)

what_to_eat = on_command("what2eat", aliases={"今天吃什么","吃什么"}, priority=5)
@what_to_eat.handle()
async def _(event: GroupMessageEvent):
    ans = await what2eat()
    await what_to_eat.finish("推荐您今天吃：\n" + ans)