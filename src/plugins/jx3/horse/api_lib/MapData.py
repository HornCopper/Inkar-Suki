from __future__ import annotations
from src.tools.dep import *

class MapPointData:
    '''关键点数据
        # 地图匹配数据，dict[ 地图id:地图中关键点位置[ 序号:数据 ] ]
        # 数据: Name,StartX,StartY,Scale,Width,Height
    '''
    startX: int
    startY: int  # 坐标点
    scale: float  # 缩放比例
    width: int
    height: int

    def __init__(self, data: dict) -> None:
        self.startX = data.get('startX') or 0
        self.startY = data.get('startY') or 0
        self.scale = data.get('Scale') or 0.0
        self.width = data.get('Width') or 0
        self.height = data.get('Height') or 0

    def to_dict(self):
        return {
            'x': self.startX,
            'y': self.startY,
            'width': self.width,
            'height': self.height,
            'scale': self.scale
        }


class MapData(StaticLoader):
    '''地图数据'''
    map_id: int  # 地图id
    map_name: str  # 地图名称
    points: dict[str, MapPointData]  # 序号:关键点
    resource_url = 'https://img.jx3box.com//map/data/map_scales.json'

    def __init__(self, map_id: str, data: dict) -> None:
        self.map_id = map_id
        first = data.get('0')
        self.map_name = first and first.get('Name')
        self.points = dict([[x, MapPointData(data[x])] for x in data])

    def to_dict(self):
        return {
            'id': self.map_id,
            'name': self.map_name,
            'points': [self.points[x].to_dict() for x in self.points]
        }
