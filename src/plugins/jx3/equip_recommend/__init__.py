from src.plugins.help import css
from src.tools.generate import generate, get_uuid
from src.constant.jx3 import aliases

from .api import *

school_mapping = {
    "傲血战意": 10026,
    "铁牢律": 10062,
    "花间游": 10021,
    "离经易道": 10028,
    "紫霞功": 10014,
    "太虚剑意": 10015,
    "冰心诀": 10081,
    "云裳心经": 10080,
    "易筋经": 10003,
    "洗髓经": 10002,
    "问水诀": 10144,
    "山居剑意": 10145,
    "笑尘诀": 10268,
    "焚影圣诀": 10242,
    "明尊琉璃体": 10243,
    "毒经": 10175,
    "补天诀": 10176,
    "惊羽诀": 10224,
    "天罗诡道": 10225,
    "铁骨衣": 10389,
    "分山劲": 10390,
    "莫问": 10447,
    "相知": 10448,
    "北傲诀": 10464,
    "凌海诀": 10533,
    "隐龙诀": 10585,
    "太玄经": 10615,
    "无方": 10627,
    "灵素": 10626,
    "孤锋诀": 10698
}

equip_recmd = on_command("jx3_eqrec", aliases={"配装"}, priority=5)


@equip_recmd.handle()
async def eqrec(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await equip_recmd.finish("唔……参数数量有问题哦，请检查后重试~\n或查看帮助文件（+help）获得更详细的信息哦~")
    kf = aliases(arg[0])
    condition = []
    if len(arg) == 2:
        condition = arg[1].split(";")
    if kf not in list(school_mapping):
        await equip_recmd.finish("唔……未找到该心法，请检查后重试~")
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
        await equip_recmd.finish("唔……音卡的配装列表图生成失败了捏，请联系作者~")
    else:
        await equip_recmd.send(MessageSegment.image(Path(img).as_uri()))


@equip_recmd.got("index", prompt="请选择配装查看哦，回复我只需要数字就行啦！")
async def equip_recmded(state: T_State, index: Message = Arg()):
    index = index.extract_plain_text()
    if checknumber(index) == False:
        await equip_recmd.finish(PROMPT_NumberInvalid)
    data = state["data"][int(index)]
    author = state["author"][int(index)]
    tag = state["tag"][int(index)]
    name = state["name"][int(index)]
    kungfu = state["kungfu"]
    data = await get_single_recequips(data, author, name, tag, kungfu)
    if type(data) == type([]):
        await equip_recmd.finish(data[0])
    else:
        await equip_recmd.finish(MessageSegment.image(Path(data).as_uri()))
