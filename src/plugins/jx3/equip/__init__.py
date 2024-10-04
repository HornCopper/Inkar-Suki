from pathlib import Path
from jinja2 import Template

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from src.const.prompts import PROMPT
from src.const.jx3.kungfu import Kungfu
from src.const.path import TEMPLATES, build_path
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.analyze import check_number
from src.utils.network import Request

from ._template import template_recommend_equip, table_recommend_head

from .api import get_recommended_equips_list, get_single_recommend_equips

RecommendEquipMatcher = on_command("jx3_equip_recommend", aliases={"配装"}, force_whitespace=True, priority=5)

@RecommendEquipMatcher.handle()
async def _(event: GroupMessageEvent, state: T_State, full_argument: Message = CommandArg()):
    if full_argument.extract_plain_text() == "":
        return
    args = full_argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2]:
        await RecommendEquipMatcher.finish(PROMPT.ArgumentCountInvalid)
    condition = []
    classic = ["PVE", "PVP"]
    if len(args) == 2:
        if args[0].upper() in classic:
            kungfu = Kungfu(args[1])
            condition.append(args[0].upper())
        else:
            kungfu = Kungfu(args[0])
            condition.append(args[1].upper())
    elif len(args) == 1:
        kungfu = Kungfu(args[0])
    if kungfu.name is None:
        await RecommendEquipMatcher.finish(PROMPT.KungfuNotExist)
    force_id = kungfu.id
    data = await get_recommended_equips_list(str(force_id), condition)
    state["data"], state["name"], state["tag"], state["author"], like = data
    state["kungfu"] = kungfu.name
    chart = []
    for i in range(len(data[1])):
        chart.append(
            Template(template_recommend_equip).render(
                num = str(i),
                author = data[3][i],
                name = data[1][i],
                tag = data[2][i],
                like = like[i]
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = f" · 配装器 · {kungfu.name}",
            additional_css = Path(
                build_path(
                    TEMPLATES,
                    [
                        "jx3",
                        "achievements_v2.css"
                    ]
                )
            ).as_uri(),
            table_head = table_recommend_head,
            table_body = "\n".join(chart)
        )
    )
    img = await generate(html, "table", False)
    img = Path(img).as_uri()
    await RecommendEquipMatcher.send(ms.image(Request(img).local_content))

@RecommendEquipMatcher.got("num", prompt="请选择配装查看哦，回复我只需要数字就行啦！")
async def _(state: T_State, num: Message = Arg()):
    index = num.extract_plain_text()
    if not check_number(index):
        await RecommendEquipMatcher.finish(PROMPT.NumberInvalid)
    data = state["data"][int(index)]
    author = state["author"][int(index)]
    tag = state["tag"][int(index)]
    name = state["name"][int(index)]
    kungfu = state["kungfu"]
    data = await get_single_recommend_equips(data, author, name, tag, kungfu)
    if isinstance(data, list):
        await RecommendEquipMatcher.finish(data[0])
    elif isinstance(data, str):
        await RecommendEquipMatcher.finish(ms.image(Request(data).local_content))