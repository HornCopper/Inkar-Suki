from src.tools.utils import *

from ..Jx3Icon import *


class QixueIcon(Jx3Icon):
    ...


class Qixue:
    def __init__(self, data: dict) -> None:
        self.load_data(data)

    def map_data(self, data: dict):
        return data

    def load_data(self, data: dict):
        self.map_data(data)
        self.name = data.get('name')
        self.icon = QixueIcon(data.get('icon'))
        self.skill_id = data.get('skill_id')

    @property
    def icon_img(self):
        return QixueIcon.from_icon(self.icon)

    def __str__(self) -> str:
        return f'[{self.name}]({self.skill_id})'

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self):
        return {
            'name': self.name,
            'icon': self.icon.filename,
            'skill_id': self.skill_id,
        }
