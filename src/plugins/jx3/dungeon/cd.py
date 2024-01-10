from src.tools.dep import *
from src.tools.generate import *
from src.plugins.help import css

from .api import *

jx3_cmd_jx3_rare_gain = on_command(
    "特殊掉落",
    aliases={
        "cd"
    },
    example=[
        Jx3Arg(Jx3ArgsType.server, is_optional=True),
        Jx3Arg(Jx3ArgsType.property),
    ],
    priority=5
)


@jx3_cmd_jx3_rare_gain.handle()
async def jx3_rare_gain(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    """
    获取部分特殊物品的上次记录：

    Notice：数据来源@茗伊插件集 https://www.j3cx.com

    Example：-cd 幽月轮 归墟玄晶
    """
    arg_server, arg_name = args
    if not arg_server:
        return await jx3_cmd_jx3_rare_gain.finish(PROMPT_ServerNotExist)
    if not arg_name:
        return await jx3_cmd_jx3_rare_gain.finish("没有输入物品名称哦")
    msg = await get_cd(arg_server, arg_name)
    return await jx3_cmd_jx3_rare_gain.finish(msg)
