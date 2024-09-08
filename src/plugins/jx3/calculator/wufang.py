# DPS计算器 无方

from typing import Optional
from jinja2 import Template
from pathlib import Path

from src.constant.jx3 import color_list

from src.tools.basic.server import server_mapping
from src.tools.basic.prompts import PROMPT
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.utils.file import read, write
from src.tools.generate import generate, get_uuid

from src.plugins.jx3.bind.role import get_player_local_data

from .online_calculator import get_calculated_data

msgbox_wufang = """
<div class="element">
    <div class="cell-title"><span>理论DPS</span></div>
    <div class="cell">{{ dps }}</div>
</div>"""

template_calculator_wufang = """
<tr>
    <td class="short-column">{{ skill }}</td>
    <td class="short-column">
        <div class="progress-bar" style="margin: 0 auto;">
            <div class="progress" style="width: {{ display }};"></div>
            <span class="progress-text">{{ percent }}</span>
        </div>
    </td>
    <td class="short-column">{{ count }}</td>
    <td class="short-column">{{ value }}</td>
</tr>"""

async def generate_calculator_img_wufang(server: Optional[str], name: str, group_id: str = ""):
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT.ServerNotExist]
    role_data = await get_player_local_data(role_name=name, server_name=server)
    if role_data.format_jx3api()["code"] != 200:
        return [PROMPT.PlayerNotExist]
    data = await get_calculated_data(server, name, group_id, "无方")
    if not data:
        return ["唔……无法计算玩家数据！请检查装备、属性、职业！"]
    stake_data = data["data"]["木桩计算结果"]
    result = stake_data["秒伤"]
    tables = []
    for skill_data in stake_data["技能统计显示"]:
        tables.append(
            Template(template_calculator_wufang).render(**{
                "skill": skill_data["显示名称"],
                "display": str(round(((skill_data["技能总输出"]/stake_data["总伤"]) / (stake_data["技能统计显示"][0]["技能总输出"]/stake_data["总伤"]))*100, 2)) + "%",
                "percent": str(round(skill_data["技能总输出"]/stake_data["总伤"]*100, 2)) + "%",
                "count": str(skill_data["技能数量"]) + "（" + str(round(skill_data["会心几率"]*100, 2)) + "%" + "会心）",
                "value": str(int(skill_data["技能总输出"]))
            })
        )
    html = Template(read(VIEWS + "/jx3/calculator/calculator.html")).render(**{
        "font": ASSETS + "/font/custom.ttf",
        "yozai": ASSETS + "/font/Yozai-Medium.ttf",
        "msgbox": Template(msgbox_wufang).render(**{
            "dps": result
        }),
        "tables": "\n".join(tables),
        "school": "无方",
        "color": color_list["无方"],
        "server": server,
        "name": name,
        "calculator": "在线DPS计算器 by 唐宋（循环数据作者请到计算器页面查看）<br>当前循环：避奚养荣_紫武"
    })
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()