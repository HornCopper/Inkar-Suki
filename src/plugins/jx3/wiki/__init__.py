from .api import *
from .renderer import *
jx3_cmd_wiki = on_command("jx3_wiki", aliases={"接引人"}, priority=5)


@jx3_cmd_wiki.handle()
async def jx3_wiki(state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    搜索剑三百科

    Example：-接引人 五行石
    '''
    template = [Jx3Arg(Jx3ArgsType.default)]
    [arg_keywords] = get_args(
        args.extract_plain_text(), template_args=template)
    if not arg_keywords:
        return await jx3_cmd_wiki.finish('没有说出需要接引的问题哦')
    logger.info(f'start wiki {arg_keywords}')
    result = await get_guide(arg_keywords)
    img = await render_items(arg_keywords, result.to_dict())
    return await jx3_cmd_wiki.send(ms.image(Path(img).as_uri()))
