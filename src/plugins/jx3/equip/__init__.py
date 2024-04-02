from src.plugins.help import css
from src.tools.generate import generate, get_uuid
from src.constant.jx3 import aliases

from tabulate import tabulate

from .api import *

jx3_cmd_equip_recommend = on_command("jx3_equip_recommend", aliases={"配装"}, priority=5)


@jx3_cmd_equip_recommend.handle()
async def jx3_equip_recommend_menu(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await jx3_cmd_equip_recommend.finish("唔……参数数量有问题哦，请检查后重试~\n或查看帮助文件（+help）获得更详细的信息哦~")
    condition = []
    classic = ["PVE", "PVP"]
    kf = ""
    if len(arg) == 2:
        if str.upper(arg[0]) in classic:
            kf = aliases(arg[1])
            condition.append(arg[0])
        else:
            kf = aliases(arg[0])
            condition.append(arg[1])
    school_mapping = await get_api("https://inkar-suki.codethink.cn/schoolmapping")
    if len(arg) == 2:
        condition = arg[1].split(";")
    if kf not in list(school_mapping):
        await jx3_cmd_equip_recommend.finish("唔……未找到该心法，请检查后重试~")
    forceId = school_mapping[kf]
    data = await get_recommended_equips_list(str(forceId), condition)
    state["data"] = data[0]
    state["name"] = data[1]
    state["tag"] = data[2]
    state["author"] = data[3]
    state["condition"] = condition
    state["kungfu"] = kf
    chart = []
    chart.append(["序号", "作者", "名称", "标签", "点赞"])
    for i in range(len(data[1])):
        chart.append([str(i), data[3][i], data[1][i], data[2][i], data[4][i]])
    html = css + tabulate(chart, tablefmt="unsafehtml")
    final_path = f"{CACHE}/{get_uuid()}.html"
    write(final_path, html)
    img = await generate(final_path, False, "table", False)
    if img == False:
        await jx3_cmd_equip_recommend.finish("唔……音卡的配装列表图生成失败了捏，请联系作者~")
    else:
        await jx3_cmd_equip_recommend.send(ms.image(Path(img).as_uri()))


@jx3_cmd_equip_recommend.got("index", prompt="请选择配装查看哦，回复我只需要数字就行啦！")
async def jx3_equip_recommend_detail(state: T_State, index: Message = Arg()):
    index = index.extract_plain_text()
    if checknumber(index) == False:
        await jx3_cmd_equip_recommend.finish(PROMPT_NumberInvalid)
    data = state["data"][int(index)]
    author = state["author"][int(index)]
    tag = state["tag"][int(index)]
    name = state["name"][int(index)]
    kungfu = state["kungfu"]
    data = await get_single_recequips(data, author, name, tag, kungfu)
    if type(data) == type([]):
        await jx3_cmd_equip_recommend.finish(data[0])
    else:
        await jx3_cmd_equip_recommend.finish(ms.image(Path(data).as_uri()))