from __future__ import annotations
from src.tools.dep.api import *
from enum import Enum


async def check_bind(id: str):
    data = await get_item_info_by_id(id)
    bind_type = data.get('BindType') or 0
    level = data.get('Level')
    return bind_type, level


async def get_item_info_by_id(id: str):
    item_info_url = f"https://helper.jx3box.com/api/wiki/post?type=item&source_id={id}"
    raw_data = await get_api(item_info_url)
    if raw_data.get('code') != 200:
        return f'获取物品信息失败了：{raw_data.get("message")}'
    return raw_data.get('data').get('source')

GoodsBindTypeBindTypes = ["未知", "不绑定", "装备后绑定", "拾取后绑定"]


class GoodsBindType(Enum):

    UnKnown = 0
    UnBind = 1
    BindOnUse = 2
    BindOnPick = 3


class GoodsInfo(dict):
    def __init__(self, data: dict = None) -> None:
        if data is None:
            data = {}
        self.id = data.get('id')
        self._bind_type: GoodsBindType = GoodsBindType.BindOnPick
        self.bind_type = data.get('bind_type') or GoodsBindType.UnKnown
        self.icon = data.get('IconID') or 18888  # 默认给个小兔兔
        self.quality = data.get('Quality')
        self.ui_id = data.get('UiID')
        self.name = data.get('Name') or '未知物品'
        self.level = data.get('Level')  # 品数（仅武器才有）
        '''被使用的次数，次数多的优先前置'''
        self.u_popularity = data.get('u_popularity') or 0
        super().__init__()

    def __str__(self) -> str:
        x = '※' * (self.quality + 1)
        return f'{x}{self.name}({self.id}){self.bind_type_str}'

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def priority(self) -> int:
        v_bind = 1 if self.bind_type == GoodsBindType.BindOnPick else 0
        v_create_id = self.ui_id or 0
        return 1e8 * self.u_popularity - v_bind * 1e12 + v_create_id

    @property
    def bind_type(self) -> GoodsBindType:
        if isinstance(self._bind_type, GoodsBindType):
            return self._bind_type
        self._bind_type = GoodsBindType(self._bind_type)
        return self._bind_type

    @bind_type.setter
    def bind_type(self, v: GoodsBindType):
        if v is None:
            self._bind_type = GoodsBindType.BindOnPick  # default
            return
        self._bind_type = v

    @property
    def img_url(self):
        return f"https://icon.jx3box.com/icon/{self.icon}.png"

    @property
    def html_code(self):
        return f"<img src={self.img_url}></img>"

    @property
    def color(self):
        '''
        根据品质返回 老灰、灰、绿、蓝、紫、金、红
        '''
        return ['rgb(220,220,220)', 'rgb(190,190,190)', 'rgb(0, 210, 75)', 'rgb(0, 126, 255)', 'rgb(254, 45, 254)', 'rgb(255, 165, 0)', '#ff0000'][self.quality]

    def to_row(self):
        new = [self.id, self.name, self.bind_type_str, self.html_code]
        return new

    @property
    def bind_type_str(self):
        return GoodsBindTypeBindTypes[self.bind_type.value]

    def __repr__(self) -> str:
        return json.dumps(self.__dict__)

    def to_dict(self) -> dict:
        r = self.__dict__
        r['img_url'] = self.img_url
        r['color'] = self.color
        r['bind_type_str'] = self.bind_type_str
        return r


class GoodsInfoFull(GoodsInfo):
    def __init__(self, data: dict = None) -> None:
        super().__init__(data)
        self.typeLabel = data.get('TypeLabel')  # 分类
        self.desc = data.get('Desc')  # 描述
        self.maxDurability = data.get('MaxDurability')  # 最大耐久
        self.maxExistAmount = get_number(
            data.get('MaxExistAmount')) or None  # 最大拥有数
        self.attributes = json.loads(data.get('attributes') or '[]')  # 包含属性
        self.recovery_price = data.get('Price')  # 回收价
        self.level = data.get('Level')  # 品数（仅武器才有）
