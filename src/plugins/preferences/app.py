from typing import Any
from jinja2 import Template

from src.const.path import ASSETS, TEMPLATES, build_path
from src.utils.file import read
from src.utils.database import db
from src.utils.database.classes import PersonalSettings
from src.utils.generate import generate
from src.templates import get_saohua
from src.utils.ui_theme import DEFAULT_UI_COLOR, normalize_ui_color

from ._template import template_preferences

import json

class Preference:
    mapping = {
        "属性": "attribute",
        "主题": "theme",
        "UI颜色": "ui_color",
        "交易行": "trade",
        "奇遇": "serendipity",
        "匿名分析": "anonymous",
        "计算器来源": "calculate_source",
        "计算器增益": "income",
        "计算器阵眼": "formation",
        "黑本显示": "random_loot_display",
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
        self.available = (
            key in self.mapping
            and key in self.data
            and hasattr(self.current, self.mapping[key])
        )

    def get(self) -> str:
        if not self.available:
            return "未找到相关偏好项！"
        result: str = getattr(self.current, self.mapping[self.key])
        return "\n".join(
            [
                f"当前{self.key}的偏好为：{result}",
                self._format_available_values(),
                self._format_setting_examples(),
            ]
        )

    def _format_available_values(self) -> str:
        if self.key == "UI颜色":
            return "可选偏好：默认，或六位十六进制颜色 #RRGGBB（例如 #7B61B5）。"
        lines = ["可选偏好："]
        for value, description in self.data[self.key].items():
            lines.append(f"- {value}：{description}")
        return "\n".join(lines)

    def _format_setting_examples(self) -> str:
        if self.key == "UI颜色":
            return "设置示例：\n偏好 UI颜色 #7B61B5\n偏好 UI颜色 默认"
        lines = ["设置示例："]
        values = list(self.data[self.key])
        if self.key == "计算器阵眼":
            values = values[:2]
        for value in values:
            lines.append(f"偏好 {self.key} {value}")
        return "\n".join(lines)
        
    def set(self) -> str:
        if not self.available:
            return "未找到相关偏好项！"
        value = normalize_ui_color(self.value) if self.key == "UI颜色" else self.value
        if value is None or (self.key != "UI颜色" and value not in self.data[self.key]):
            return "该偏好不满足可选值，请先发送“偏好”查看所有可用值！"
        setattr(self.current, self.mapping[self.key], value)
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
            current = self.setting(m)
            values = (
                {DEFAULT_UI_COLOR: current == DEFAULT_UI_COLOR, "#RRGGBB": False}
                if m == "UI颜色" else {v: v == current for v in self.data[m]}
            )
            if m == "UI颜色" and current != DEFAULT_UI_COLOR:
                values[current] = True
            preferences.append(
                Template(
                    template_preferences
                ).render(
                    name = m,
                    values = values,
                    preferences = self.data[m]
                )
            )
        html = Template(
            read(TEMPLATES + "/preferences.html")
        ).render(
            font = ASSETS + "/font/PingFangSC-Semibold.otf",
            prefeernce_items = preferences,
            saohua = get_saohua()
        )
        return await generate(html, ".preference-container", segment=True)
