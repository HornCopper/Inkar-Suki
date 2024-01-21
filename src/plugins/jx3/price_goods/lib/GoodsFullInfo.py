from .GoodsBase import *
from .GoodsPrice import *
from src.tools.dep.common_api.none_dep_api import *


class GoodsInfoFull(GoodsInfo):
    def __init__(self, data: dict = None) -> None:
        if data is None:
            return
        super().__init__(data)

    def to_dict(self) -> dict:
        r = super().to_dict()
        self_dict = {
            'typeLabel': self.typeLabel,
            'desc': self.desc,
            'maxDurability': self.maxDurability,
            'maxExistAmount': self.maxExistAmount,
            'attributes': self.attributes,
            'recovery_price': self.recovery_price,
            'level': self.level,
            'wucai_properties': [x.to_dict() for x in self.wucai_properties],
        }
        r.update(self_dict)
        return r

    def map_data(self, data: dict):
        if 'TypeLabel' not in data:
            return
        data['typeLabel'] = data.get("TypeLabel")  # 分类
        data['desc'] = data.get("Desc")  # 描述
        data['maxDurability'] = data.get("MaxDurability")  # 最大耐久
        data['maxExistAmount'] = data.get("MaxExistAmount")    # 最大拥有数
        data['attributes'] = data.get("attributes") or []  # 包含属性
        data['recovery_price'] = data.get("Price")  # 回收价
        data['level'] = data.get("Level")  # 品数（仅武器才有）

        wucai_data = data.get("WuCaiHtml") or ""  # 五彩石属性
        wucai_properties = WucaiAttribute.from_html(wucai_data)  # convert to wucai-properties
        data['wucai_properties'] = wucai_properties
        return super().map_data(data)

    def load_data(self, data: dict):
        super().load_data(data)
        self.typeLabel = data.get("typeLabel")  # 分类
        self.desc = data.get("desc")
        self.maxDurability = data.get("maxDurability")
        self.maxExistAmount = get_number(data.get("maxExistAmount")) or None
        self.attributes = json.loads(data.get("attributes") or "[]")
        self.recovery_price = data.get("recovery_price")
        self.level = data.get("level")
        self.wucai_properties = data.get("wucai_properties")
        return self

    @classmethod
    def from_dict(cls, data: dict):
        target = GoodsInfoFull(data)
        if data.get('price'):
            target.price = dict2obj(GoodsPriceSummary(), data.get('price'))
        if data.get('current_price'):
            target.current_price = dict2obj(GoodsPriceDetail(), data.get('current_price'))

        return target
