from typing import Any
from jinja2 import Template

from src.const.path import ASSETS, TEMPLATES, build_path
from src.utils.file import read
from src.utils.database import db
from src.utils.database.classes import PersonalSettings
from src.utils.generate import generate

from ._template import template_preferences

import json

class Preference:
    mapping = {
        "属性": "attribute",
        "主题": "theme",
        "交易行": "trade",
        "奇遇": "serendipity",
        "匿名分析": "anonymous",
        "计算器增益": "income",
        "计算器阵眼": "formation"
    }

    def __init__(self, user_id: int, key: str = "", value: str = ""):
        self.data: dict[str, dict[str, str]] = json.loads(
            read(build_path(ASSETS, ["source", "preference", "preferences.json"]))
        )
        current_settings: PersonalSettings | Any = db.where_one(PersonalSettings(), "user_id = ?", str(user_id), default=PersonalSettings(user_id=user_id))
        self.settings = current_settings
        self.current = current_settings.setting
        self.key = key
        self.value = value
        self.available = hasattr(self.current, self.mapping[self.key]) if key != "" else False

    def get(self) -> str:
        if not self.available:
            return "未找到相关偏好项！"
        result: str = getattr(self.current, self.mapping[self.key])
        return f"当前{self.key}的偏好为：{result}"       
        
    def set(self) -> str:
        if not self.available:
            return "未找到相关偏好项！"
        if self.value not in self.data[self.key].keys():
            return "该偏好不满足可选值，请先发送“偏好”查看所有可用值！"
        setattr(self.current, self.mapping[self.key], self.value)
        self.settings.setting = self.current
        db.save(self.settings)
        return "已保存个人偏好！\n发送“偏好”查看所有偏好！\n发送“偏好 偏好项”查看某一项的设定！"

    def setting(self, key: str) -> str:
        result: str = getattr(self.current, self.mapping[key])
        return result
    
    async def query(self):
        """
        获得个人偏好图
        """
        preferences = []
        for m in self.mapping:
            preferences.append(
                Template(
                    template_preferences
                ).render(
                    name = m,
                    values = {
                        v: v == self.setting(m)
                        for v in self.data[m].keys()
                    },
                    preferences = self.data[m]
                )
            )
        html = Template(
            read(TEMPLATES + "/preferences.html")
        ).render(
            font = ASSETS + "/font/PingFangSC-Semibold.otf",
            prefeernce_items = preferences
        )
        return await generate(html, ".preference-container", segment=True)