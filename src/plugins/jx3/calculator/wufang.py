# DPS计算器 无方

from jinja2 import Template
from pathlib import Path

from src.const.prompts import PROMPT
from src.const.path import ASSETS, build_path
from src.const.jx3.kungfu import Kungfu
from src.templates import SimpleHTML
from src.utils.database.player import search_player
from src.utils.generate import generate

from .online_calculator import get_calculated_data
from ._template import template_calculator_wufang, msgbox_wufang

async def generate_calculator_img_wufang(server: str, name: str):
    role_data = await search_player(role_name=name, server_name=server)
    if role_data.format_jx3api()["code"] != 200:
        return [PROMPT.PlayerNotExist]
    data = await get_calculated_data(server, name, "无方")
    if not data:
        return [PROMPT.CalculatorValueInvalid]
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
    html = str(
        SimpleHTML(
            html_type = "jx3",
            html_template = "calculator",
            **{
                "font": build_path(ASSETS, ["font", "custom.ttf"]),
                "yozai": build_path(ASSETS, ["font", "Yozai-Medium.ttf"]),
                "msgbox": Template(msgbox_wufang).render(**{
                    "dps": result
                }),
                "tables": "\n".join(tables),
                "school": "无方",
                "color": Kungfu("无方").color,
                "server": server,
                "name": name,
                "calculator": "在线DPS计算器 by 唐宋（循环数据作者请到计算器页面查看）<br>当前循环：避奚养荣_紫武"
            }
        )
    )
    final_path = await generate(html, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()