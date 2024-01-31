from src.plugins.help import css
from src.tools.generate import generate, get_uuid
from src.constant.jx3 import aliases, std_kunfu

from .api import *


jx3_cmd_equip_recommend = on_command(
    "jx3_equip_recommend",
    aliases={"配装"},
    priority=5,
    example=[
        Jx3Arg(Jx3ArgsType.kunfu),
        Jx3Arg(Jx3ArgsType.string, alias="分类", is_optional=True)
    ]
)

__static_dict = {
    "pve": "PVE",
    "pvp": "PVP",
}


@jx3_cmd_equip_recommend.handle()
async def jx3_equip_recommend_menu(event: GroupMessageEvent, state: T_State, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_kunfu, arg_condition = args
    condition = arg_condition.split(";") if arg_condition else []
    condition = [__static_dict.get(str.lower(x)) or x for x in condition]
    if not arg_kunfu:
        return await jx3_cmd_equip_recommend.finish(f"唔……未找到名字叫[{arg_kunfu}]的心法，请检查后重试~")
    forceId = arg_kunfu.gameid
    data = await get_recommended_equips_list(str(forceId), condition)
    state["data"] = data[0]
    state["name"] = data[1]
    state["tag"] = data[2]
    state["author"] = data[3]
    state["condition"] = condition
    state["kungfu"] = arg_kunfu.name
    chart = []
    chart.append(["序号", "作者", "名称", "标签", "点赞"])
    for i in range(len(data[1])):
        chart.append([str(i), data[3][i], data[1][i], data[2][i], data[4][i]])
    html = css + tabulate(chart, tablefmt="unsafehtml")
    final_path = f"{bot_path.CACHE}/{get_uuid()}.html"
    write(final_path, html)
    img = await generate(final_path, False, "table", False)
    if not img:
        return await jx3_cmd_equip_recommend.finish(f"唔……{Config.name}的配装列表图生成失败了捏，请联系作者~")
    return await jx3_cmd_equip_recommend.send(ms.image(Path(img).as_uri()))


@jx3_cmd_equip_recommend.got("index", prompt="请选择配装查看哦，回复我只需要数字就行啦！")
async def equip_recmded(event: GroupMessageEvent, state: T_State, index: Message = Arg()):
    index = index.extract_plain_text()
    if checknumber(index) is False:
        return await jx3_cmd_equip_recommend.finish(PROMPT_NumberInvalid)
    data = state["data"][int(index)]
    author = state["author"][int(index)]
    tag = state["tag"][int(index)]
    name = state["name"][int(index)]
    kungfu = state["kungfu"]
    data = await get_single_recequips(data, author, name, tag, kungfu)
    if isinstance(data, list):
        return await jx3_cmd_equip_recommend.finish(data[0])
    return await jx3_cmd_equip_recommend.send(ms.image(Path(data).as_uri()))
