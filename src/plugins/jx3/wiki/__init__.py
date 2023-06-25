from .api import *
from .renderer import *
jx3_cmd_wiki = on_command("jx3_wiki", aliases={"接引人"}, priority=5)


@jx3_cmd_wiki.handle()
async def jx3_wiki(state: T_State, event: GroupMessageEvent, arg: Message = Arg()):
    '''
    搜索剑三百科

    Example：-百科 五行石
    '''
    template = [Jx3Arg(Jx3ArgsType.default)]
    args = get_args(arg.extract_plain_text(), template_args=template)
    [arg_keywords] = args
    result = await get_guide(arg_keywords)
    img = await render_items(arg_keywords, result.to_dict())
    return await jx3_cmd_wiki.send(ms.image(Path(img).as_uri()))
