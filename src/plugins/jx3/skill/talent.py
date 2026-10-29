from typing import Literal
from pydantic import BaseModel
from pathlib import Path
from jinja2 import Template

from nonebot.adapters.onebot.v11 import Message, MessageSegment as ms

from src.const.jx3.kungfu import Kungfu
from src.const.path import build_path, TEMPLATES
from src.templates import HTMLSourceCode
from src.utils.jx3_data import talent_data
from src.utils.network import Request
from src.utils.generate import generate

from ._template import template_body_talent, table_head_talent

import html as HTML

class QixueInfo(BaseModel):
    icon: str = ""
    name: str = ""
    desc: str = ""
    location: tuple[int, int] = (0, 0)

class Qixue:

    def __init__(self, qixue: str, kungfu: str, season: str = "", data: dict | None = None):
        self.name = qixue
        self.kungfu = kungfu
        self.season = season
        self.qixue_data = data or {}

    @classmethod
    async def create(cls, qixue: str, kungfu: str, season: str) -> "Qixue | Literal[False]":
        """异步创建实例，并确保 qixue_data 被初始化"""
        data = await cls.get_qixue_data(season)
        if not data:
            return False
        return cls(qixue, kungfu, season, data)

    @staticmethod
    async def get_qixue_data(season: str = "") -> dict | Literal[False]:
        return talent_data(season) or False

    @property
    def info(self) -> list[QixueInfo]:
        results = []
        kungfu_qixue = self.qixue_data.get(self.kungfu, {})
        for x in kungfu_qixue:
            for y in kungfu_qixue[x]:
                if isinstance(kungfu_qixue[x][y], dict) and self.name in kungfu_qixue[x][y].get("name", ""):
                    data = kungfu_qixue[x][y]
                    results.append(
                        QixueInfo(
                            icon = "https://icon.jx3box.com/icon/" + str(data["icon"]) + ".png",
                            name = data["name"],
                            desc = data["desc"],
                            location = (int(x), int(y)),
                        ),
                    )
        return results

def safe_format_desc(desc: str) -> str:
    desc = desc.replace("&lt;", "<").replace("&gt;", ">")
    desc = desc.replace("<", "&lt;").replace(">", "&gt;")
    return desc

async def get_talent_info(name: str, kungfu: str, season: str = "") -> str | Message | ms:
    kungfu_name = Kungfu(kungfu).name
    if kungfu_name is None:
        return "无法识别该心法，请检查后重试！\n参考格式：奇穴 心法 关键词\n奇穴 心法 关键词 赛季名\n奇穴 心法 赛季名\n奇穴 心法\n赛季名可使用【v+日期】，例如 v20260413，若报错说明当天无数据，请往前调整一天。"
    talents = await Qixue.create(name, kungfu_name, season)
    if not talents:
        return "本地没有该版本的奇穴快照，请检查版本名称，或省略版本查询最新奇穴。"
    talents = talents.info
    if len(talents) == 0:  # No match
        return "没有找到任何匹配的奇穴，请检查心法或奇穴名后重试？"
    elif len(talents) == 1:  # Unique match
        response = await Request(talents[0].icon).get()
        response.raise_for_status()
        return ms.image(
            response.content,
        ) + f"第{talents[0].location[0]}重·第{talents[0].location[1]}层：{talents[0].name}\n{talents[0].desc}"
    else:  # Much match
        tables = []
        for each_talent in talents:
            tables.append(
                Template(template_body_talent).render(
                    icon = each_talent.icon,
                    name = each_talent.name,
                    location = f"第{each_talent.location[0]}重·第{each_talent.location[1]}层",
                    desc = safe_format_desc(HTML.escape(each_talent.desc)),
                ),
            )
        html = str(
            HTMLSourceCode(
                application_name = f"奇穴 · {kungfu_name} · {season or '最新'}",
                additional_js = Path(build_path(TEMPLATES, ["jx3", "qixue.js"])),
                table_head = table_head_talent,
                table_body = "\n".join(tables),
            ),
        )
        image = await generate(html, ".container", True, segment = True)
        return image
