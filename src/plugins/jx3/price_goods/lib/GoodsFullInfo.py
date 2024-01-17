from .GoodsBase import *
from .GoodsPrice import *
from src.tools.dep.common_api.none_dep_api import *


class GoodsInfoFull(GoodsInfo):
    def __init__(self, data: dict = None) -> None:
        if data is None:
            return
        self.load_data(data)
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

    def load_data(self, data: dict):
        super().load_data(data)
        self.typeLabel = data.get("TypeLabel")  # 分类
        self.desc = data.get("Desc")  # 描述
        self.maxDurability = data.get("MaxDurability")  # 最大耐久
        self.maxExistAmount = get_number(data.get("MaxExistAmount")) or None  # 最大拥有数
        self.attributes = json.loads(data.get("attributes") or "[]")  # 包含属性
        self.recovery_price = data.get("Price")  # 回收价
        self.level = data.get("Level")  # 品数（仅武器才有）
        data = data.get("WuCaiHtml") or ""  # 五彩石属性
        self.wucai_properties = WucaiAttribute.from_html(data)  # convert to wucai-properties
        return self

    @classmethod
    def from_dict(cls, data: dict):
        target = GoodsInfoFull()
        target.load_local_data(data)
        if data.get('price'):
            target.price = dict2obj(GoodsPriceSummary(), data.get('price'))
        if data.get('current_price'):
            target.current_price = dict2obj(GoodsPriceDetail(), data.get('current_price'))
        if target.current_price is not None and not hasattr(target.current_price, 'to_dict'):
            pass
        if target.price is not None and not hasattr(target.price, 'to_dict'):
            pass
        return target
