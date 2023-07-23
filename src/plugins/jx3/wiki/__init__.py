from .api import *
from .renderer import *

jx3_cmd_wiki = on_command("jx3_wiki", aliases={"接引人"}, priority=5)


@jx3_cmd_wiki.handle()
async def jx3_wiki(state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    搜索剑三百科

    Example：-接引人 五行石
    """
    template = [Jx3Arg(Jx3ArgsType.default)]
    [arg_keywords] = get_args(
        args.extract_plain_text(), template_args=template)
    if not arg_keywords:
        return await jx3_cmd_wiki.finish("没有说出需要接引的问题哦")
    logger.info(f"start wiki {arg_keywords}")
    result = await get_guide(arg_keywords)
    state["result"] = result
    img = await render_items(arg_keywords, result.to_dict())
    return await jx3_cmd_wiki.send(ms.image(Path(img).as_uri()))


@jx3_cmd_wiki.got("reference")
async def jx3_next_ques(state: T_State, event: GroupMessageEvent, reference: Message = Arg()):
    """
    提交相关项查询
    """
    template = [Jx3Arg(Jx3ArgsType.default)]
    [arg_reference] = get_args(reference.extract_plain_text(), template_args=template)
    logger.debug(f"next_ques:{arg_reference}")
    if not arg_reference:
        return
    arg_cmd = arg_reference[0:2].lower()
    logger.debug(f"next_ques cmd:{arg_cmd}")
    result = state.get("result")
    arg_index = get_number(arg_reference[2:])
    if arg_cmd == "xg" or arg_cmd == "相关":  # 相关问题
        arg_sets = result.tip.results
    elif arg_cmd == "yy" or arg_cmd == "引用":  # 引用词
        arg_sets = result.question.relateds
    else:
        return
    if len(arg_sets) <= arg_index:
        return await jx3_cmd_wiki.send(f"没有相关的引用哦,最多有{len(arg_sets)}项可选,但你选了第{arg_index+1}项")
    arg_keyword = arg_sets[arg_index]
    logger.debug(f"next_ques ({arg_index}) cmd:{arg_keyword}")
    return await jx3_wiki(state, event, obMessage(arg_keyword))
