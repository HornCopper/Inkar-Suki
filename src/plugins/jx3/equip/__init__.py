from pathlib import Path

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from src.tools.utils.file import read, write, get_content_local
from src.tools.utils.path import ASSETS, CACHE, PLUGINS, VIEWS
from src.tools.utils.num import checknumber
from src.tools.generate import generate, get_uuid
from src.tools.basic.prompts import PROMPT
from src.constant.jx3 import school_name_aliases

from .api import *

template_rec_equip = """
<tr>
    <td class="short-column">$num</td>
    <td class="short-column">$author</td>
    <td class="short-column">$name</td>
    <td class="short-column">$tag</td>
    <td class="short-column">$like</td>
</tr>"""

jx3_cmd_equip_recommend = on_command("jx3_equip_recommend", aliases={"配装"}, force_whitespace=True, priority=5)

@jx3_cmd_equip_recommend.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await jx3_cmd_equip_recommend.finish("唔……参数数量有问题哦，请检查后重试~\n或查看帮助文件（+help）获得更详细的信息哦~")
    condition = []
    classic = ["PVE", "PVP"]
    kf = ""
    if len(arg) == 2:
        if arg[0].upper() in classic:
            kf = school_name_aliases(arg[1])
            condition.append(arg[0].upper())
        else:
            kf = school_name_aliases(arg[0])
            condition.append(arg[1].upper())
    elif len(arg) == 1:
        kf = school_name_aliases(arg[0])
    school_mapping = json.loads(read(PLUGINS + "/jx3/attributes/schoolmapping.json"))
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
    for i in range(len(data[1])):
        chart.append(template_rec_equip
                     .replace("$num", str(i))
                     .replace("$author", data[3][i])
                     .replace("$name", data[1][i])
                     .replace("$tag", data[2][i])
                     .replace("$like", data[4][i]))
    html = read(VIEWS + "/jx3/equip/recommend.html")
    font = ASSETS + "/font/custom.ttf"
    chart = "\n".join(chart)
    html = html.replace("$customfont", font).replace("$tablecontent", chart).replace("$kf", kf) # type: ignore
    final_path = f"{CACHE}/{get_uuid()}.html"
    write(final_path, html)
    img = await generate(final_path, False, "table", False)
    img = Path(img).as_uri() # type: ignore
    if not img:
        await jx3_cmd_equip_recommend.finish("唔……音卡的配装列表图生成失败了捏，请联系作者~")
    else:
        img = get_content_local(img)
        await jx3_cmd_equip_recommend.send(ms.image(img))


@jx3_cmd_equip_recommend.got("index", prompt="请选择配装查看哦，回复我只需要数字就行啦！")
async def jx3_equip_recommend_detail(state: T_State, index: Message = Arg()):
    index_ = index.extract_plain_text()
    if not checknumber(index_):
        await jx3_cmd_equip_recommend.finish(PROMPT.NumberInvalid)
    data = state["data"][int(index_)] # type: ignore
    author = state["author"][int(index_)] # type: ignore
    tag = state["tag"][int(index_)] # type: ignore
    name = state["name"][int(index_)] # type: ignore
    kungfu = state["kungfu"]
    data = await get_single_recequips(data, author, name, tag, kungfu)
    if isinstance(data, list):
        await jx3_cmd_equip_recommend.finish(data[0])
    else:
        await jx3_cmd_equip_recommend.finish(ms.image(Path(data).as_uri()))