from typing import Literal
from pydantic import BaseModel
from pathlib import Path
from jinja2 import Template

from nonebot.adapters.onebot.v11 import Message, MessageSegment as ms

from src.const.jx3.kungfu import Kungfu, season as s
from src.const.path import build_path, CONST, TEMPLATES
from src.templates import HTMLSourceCode
from src.utils.network import Request
from src.utils.file import read, write
from src.utils.generate import generate

from ._template import template_body_talent, table_head_talent

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
        self.season = season

    @classmethod
    async def initialize_qixue_data(cls, season: str = "") -> bool:
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
        cls.qixue_data = {}
        status = await cls.initialize_qixue_data(season)
        if not status:
            return False
        return cls(qixue, kungfu, season)
    
    @staticmethod
    async def get_qixue_data(season: str = "") -> dict | Literal[False]:
        data = (await Request("https://data.jx3box.com/talent/std/index.json").get()).json()
        for each_ver in data:
            if (s in each_ver["name"] and season == "") or (season in each_ver["name"] and season != ""):
                path = build_path(CONST, ["cache", each_ver["version"] + ".json"])
                if os.path.exists(path):
                    return json.loads(read(path))
                qxdata = (await Request("https://data.jx3box.com/talent/std/" + each_ver["version"] + ".json").get()).json()
                write(path, json.dumps(qxdata, ensure_ascii=False))
                return qxdata
        return False
    
    @property
    def info(self) -> list[QixueInfo]:
        results = []
        kungfu_qixue = self.qixue_data[self.kungfu]
        for x in kungfu_qixue:
            for y in kungfu_qixue[x]:
                if "name" in kungfu_qixue[x][y] and self.name in kungfu_qixue[x][y]["name"]:
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
    
async def get_talent_info(name: str, kungfu: str, season: str = "") -> str | Message | ms:
    kungfu_name = Kungfu(kungfu).name
    if kungfu_name is None:
        return "无法识别该心法，请检查后重试！"
    talents = await Qixue.create(name, kungfu_name, season)
    if not talents:
        return "没有找到匹配的赛季名称，请检查赛季名称是否正确？"
    talents = talents.info
    if len(talents) == 0: # No match
        return "没有找到任何匹配的奇穴，请检查心法或奇穴名后重试？"
    elif len(talents) == 1: # Unique match
        return ms.image(talents[0].icon) + f"第{talents[0].location[0]}重·第{talents[0].location[1]}层：{talents[0].name}\n{talents[0].desc}"
    else: # Much match
        tables = []
        for each_talent in talents:
            tables.append(
                Template(template_body_talent).render(
                    icon = each_talent.icon,
                    name = each_talent.name,
                    location = f"第{each_talent.location[0]}重·第{each_talent.location[1]}层",
                    desc = each_talent.desc
                )
            )
        html = str(
            HTMLSourceCode(
                application_name = f"奇穴 · {kungfu_name} · {season or '最新'}",
                additional_js = Path(build_path(TEMPLATES, ["jx3", "qixue.js"])),
                table_head = table_head_talent,
                table_body = "\n".join(tables)
            )
        )
        image = await generate(html, ".container", True, segment=True)
        return image