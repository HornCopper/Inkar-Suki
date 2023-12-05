from src.tools.dep import *
from src.tools.generate import *
from src.plugins.help import css

from .api import *

jx3_cmd_jx3_rare_gain = on_command("jx3_rare_gain", aliases={"cd"}, priority=5)

@jx3_cmd_jx3_rare_gain.handle()
async def jx3_rare_gain(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取部分特殊物品的上次记录：

    Notice：数据来源@茗伊插件集 https://www.j3cx.com

    Example：-cd 幽月轮 归墟玄晶
    """
    template = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(Jx3ArgsType.default)]
    arg = get_args(args.extract_plain_text(), template)
    arg_server, arg_name = arg
    arg_server = server_mapping(arg_server, event.group_id)
    if not arg_name:
        return await jx3_cmd_jx3_rare_gain.finish("没有输入物品名称哦")
    msg = await get_cd(arg_server, arg_name)
    return await jx3_cmd_jx3_rare_gain.finish(msg)