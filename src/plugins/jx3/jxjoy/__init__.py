from src.tools.dep.bot import *
from .api import *

random_ = on_command("jx3_random", aliases={'骚话','烧话'}, priority=5)
@random_.handle()
async def _():
    '''
    召唤一条骚话：

    Example：-骚话
    '''
    r_text,r_id = await random__()
    await random_.finish(f'推栏之{r_id}：{r_text}')


tiangou = on_command("jx3_tiangou", aliases={"舔狗"}, priority=5)
@tiangou.handle()
async def _(event: GroupMessageEvent):
    '''
    获取一条舔狗日志：

    Example：-舔狗
    '''
    data = await tiangou_()
    await tiangou.finish(f"舔狗日志：\n{data}")