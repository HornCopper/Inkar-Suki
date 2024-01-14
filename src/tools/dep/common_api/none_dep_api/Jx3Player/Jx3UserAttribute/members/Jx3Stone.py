from .Jx3Icon import *


class Jx3Stone:
    def __init__(self, data: dict) -> None:
        if data is None:
            data = {}
        self.load_data(data)

    def map_data(self, data: dict):
        if 'Name' not in data:
            return data
        data['name'] = data.get('Name')
        data['level'] = data.get('Level') or 0
        data['icon'] = data.get('Icon')

    def load_data(self, data: dict):
        self.map_data(data)
        self.name = data.get('name')
        self.level: int = int(data.get('level'))
        self.icon = data.get('icon') and Jx3Icon(data.get('icon'))

    def to_dict(self):
        result = {
            'name': self.name,
            'level': self.level,
            'icon': self.icon.filename,
        }
        return result
