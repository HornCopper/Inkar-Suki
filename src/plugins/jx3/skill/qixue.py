from typing import Literal
from pydantic import BaseModel
from pathlib import Path
from jinja2 import Template

from nonebot.adapters.onebot.v11 import Message, MessageSegment as ms

from src.const.jx3.kungfu import Kungfu
from src.const.path import build_path, CONST, TEMPLATES
from src.templates import HTMLSourceCode
from src.utils.network import Request
from src.utils.file import read, write
from src.utils.generate import generate

from ._template import template_body, table_head

import json
import os

class QixueInfo(BaseModel):
    icon: str = ""
    name: str = ""
    desc: str = ""
    location: tuple[int, int] = (0, 0)
    

class Qixue:
    qixue_data: dict[str, dict[str, dict]] = {}

    def __init__(self, qixue: str, kungfu: str, season: str = ""):
        self.name = qixue
        self.kungfu = kungfu

    @classmethod
    async def initialize_qixue_data(cls, season) -> bool:
        """类方法，用于异步初始化 qixue_data"""
        if cls.qixue_data == {}:
            data = await cls.get_qixue_data(season)
            if not data:
                return False
            cls.qixue_data = data
            return True
        return True

    @classmethod
    async def create(cls, qixue: str, kungfu: str, season: str) -> "Qixue | Literal[False]":
        """异步创建实例，并确保 qixue_data 被初始化"""
        status = await cls.initialize_qixue_data(season)
        if not status:
            return False
        return cls(qixue, kungfu)
    
    @staticmethod
    async def get_qixue_data(season: str = "") -> dict | Literal[False]:
        data = (await Request("https://data.jx3box.com/talent/std/index.json").get()).json()
        for each_ver in data:
            if (each_ver["name"].find("体服") == -1 and season == "") or (season in each_ver["name"] and season != ""):
                path = build_path(CONST, ["cache", each_ver["version"] + ".json"])
                if os.path.exists(path):
                    return json.loads(read(path))
                qxdata = (await Request("https://data.jx3box.com/talent/" + each_ver["version"] + ".json").get()).json()
                write(path, json.dumps(qxdata, ensure_ascii=False))
                return qxdata
        return False
    
    @property
    def info(self) -> list[QixueInfo]:
        results = []
        kungfu_qixue = self.qixue_data[self.kungfu]
        for x in kungfu_qixue:
            for y in kungfu_qixue[x]:
                if self.name in kungfu_qixue[x][y]["name"]:
                    data = kungfu_qixue[x][y]
                    results.append(
                        QixueInfo(
                            icon = "https://icon.jx3box.com/icon/" + str(data["icon"]) + ".png",
                            name = data["name"],
                            desc = data["desc"],
                            location = (int(x), int(y))
                        )
                    )
        return results
    
async def get_qixue(name: str, kungfu: str, season: str = "") -> str | Message | Path:
    kungfu_name = Kungfu(kungfu).name
    if kungfu_name is None:
        return "无法识别该心法，请检查后重试！"
    info = await Qixue.create(name, kungfu, season)
    if not info:
        return "没有找到匹配的赛季名称，请检查赛季名称是否正确？"
    info = info.info
    if len(info) == 0: # No match
        return "没有找到任何匹配的奇穴，请检查心法或奇穴名后重试？"
    elif len(info) == 1: # Unique match
        return ms.image(info[0].icon) + f"第{info[0].location[0]}重·第{info[0].location[1]}层：{info[0].name}\n{info[0].desc}"
    else: # Much match
        tables = []
        for qx in info:
            tables.append(
                Template(template_body).render(
                    icon = qx.icon,
                    name = qx.name,
                    location = f"第{qx.location[0]}重·第{qx.location[1]}层",
                    desc = qx.desc
                )
            )
        html = str(
            HTMLSourceCode(
                application_name = f" 奇穴搜索 · {name} · {kungfu} · {season or '最新'}",
                additional_js = Path(build_path(TEMPLATES, ["jx3", "qixue.js"])),
                table_head = table_head,
                table_body = "\n".join(tables)
            )
        )
        image = await generate(html, "table", True)
        return Path(image)

# import asyncio
# async def main():
#     instance = await Qixue.create("", "莫问", "怒海争锋")
#     print(instance.info)
# asyncio.run(main())