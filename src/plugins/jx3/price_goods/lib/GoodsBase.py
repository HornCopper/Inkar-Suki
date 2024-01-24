from __future__ import annotations
from src.views import *
from src.tools.dep import *
from enum import Enum


async def get_item_info_by_id(id: str):
    item_info_url = f"https://helper.jx3box.com/api/wiki/post?type=item&source_id={id}"
    raw_data = await get_api(item_info_url)
    if not raw_data or raw_data.get("code") != 200:
        msg = (raw_data and raw_data.get("message")) or "无数据"
        return f"获取物品信息失败了：{msg}"
    return raw_data.get("data").get("source")

GoodsBindTypeBindTypes = ["未知", "不绑定", "装备后绑定", "拾取后绑定"]


class GoodsBindType(Enum):
    UnKnown = 0
    UnBind = 1
    BindOnUse = 2
    BindOnPick = 3


class GoodsInfo(dict):
    def init_computed_props(self):
        self.price = None  # PriceSummary
        self.current_price = None  # PriceDetail

    async def reload_data(self, data: dict):
        item_id = data.get('id')
        new_data = await get_item_info_by_id(item_id)
        if new_data is not None and isinstance(new_data, dict):
            data.update(new_data)
        else:
            logger.warning(f'invalid goods-detail data occurred:{item_id}->{new_data}')
        self.load_data(data)

    def __init__(self, data: dict = None, not_to_load: bool = False) -> None:
        super().__init__()
        if data is None:
            data = {}  # 默认给个空数据用于初始化一个模板
        if not_to_load:
            return
        self.load_data(data)

    def __str__(self) -> str:
        x = "※" * (self.quality + 1)
        return f"{x}{self.name}({self.id}){self.attribute_desc or ''}{self.bind_type_str}"

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
        """
        根据品质返回 老灰、灰、绿、蓝、紫、金、红
        """
        if not self.quality:
            return 'rgb(0,0,0)'
        rng = ["rgb(220,220,220)", "rgb(190,190,190)", "rgb(0, 210, 75)",
               "rgb(0, 126, 255)", "rgb(254, 45, 254)", "rgb(255, 165, 0)", "#ff0000"]
        if len(rng) <= self.quality:
            return 'rgb(255,0,0)'
        return rng[self.quality]

    def to_row(self):
        new = [self.id, self.name, self.bind_type_str, self.html_code]
        return new

    @property
    def bind_type_str(self):
        return GoodsBindTypeBindTypes[self.bind_type.value]

    def load_data(self, data: dict):
        self.map_data(data)
        self.init_computed_props()

        self.id = data.get("id")
        self._bind_type: GoodsBindType = GoodsBindType.BindOnPick
        self.bind_type = data.get("bind_type") or GoodsBindType.UnKnown
        """被使用的次数，次数多的优先前置"""
        self.u_popularity = data.get("u_popularity") or 0

        self.icon = data.get("icon") or 18888  # 默认给个小兔兔
        self.quality = data.get("quality")
        self.ui_id = data.get("ui_id")
        self.name = data.get("name") or "未知物品"
        self.level = data.get("level")  # 品数（仅装备才有）
        self.attribute_desc: str = data.get('attribute_desc')  # 属性描述，根据属性算出（仅装备才有）
        return self

    def map_data(self, data: dict):
        if 'IconID' not in data:
            return data
        attributes = data.get('attributes') or '[]'
        attributes = attributes if isinstance(attributes, list) else json.loads(attributes)
        attr_labels = [x.get('label') for x in attributes]
        attr_primary = [Jx3EquipAttribute(x).primary_attribute for x in attr_labels]
        data['attribute_desc'] = Jx3Equip.get_primary_attribute(attr_primary)

        data['icon'] = data.get("IconID") or 18888  # 默认给个小兔兔
        data['quality'] = data.get("Quality")
        data['ui_id'] = data.get("UiID")
        data['name'] = data.get("Name") or "未知物品"
        data['level'] = data.get("Level")  # 品数（仅装备才有）

    def to_dict(self) -> dict:
        return {
            'img_url': self.img_url,
            'color': self.color,
            'bind_type_str': self.bind_type_str,
            'bind_type': self.bind_type.value,
            'html_code': self.html_code,
            'id': self.id,
            'icon': self.icon,
            'quality': self.quality,
            'ui_id': self.ui_id,
            'name': self.name,
            'level': self.level,
            'attribute_desc': self.attribute_desc,
            'u_popularity': self.u_popularity,
            'price': (self.price.to_dict() if hasattr(self.price, 'to_dict') else self.price) if self.price else None,
            'current_price': (self.current_price.to_dict() if hasattr(self.current_price, 'to_dict') else self.current_price) if self.current_price else None,
        }
