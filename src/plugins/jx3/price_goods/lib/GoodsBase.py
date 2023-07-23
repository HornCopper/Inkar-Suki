from __future__ import annotations
import copy
import re
from src.views import *
from src.tools.dep import *
from enum import Enum


async def check_bind(id: str):
    data = await get_item_info_by_id(id)
    bind_type = data.get("BindType") or 0
    level = data.get("Level")
    return bind_type, level


async def get_item_info_by_id(id: str):
    item_info_url = f"https://helper.jx3box.com/api/wiki/post?type=item&source_id={id}"
    raw_data = await get_api(item_info_url)
    if raw_data.get("code") != 200:
        msg = raw_data.get("message")
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

    def __init__(self, data: dict = None) -> None:
        self.init_computed_props()
        if data is None:
            data = {}
        self.id = data.get("id")
        self._bind_type: GoodsBindType = GoodsBindType.BindOnPick
        self.bind_type = data.get("bind_type") or GoodsBindType.UnKnown
        self.icon = data.get("IconID") or 18888  # 默认给个小兔兔
        self.quality = data.get("Quality")
        self.ui_id = data.get("UiID")
        self.name = data.get("Name") or "未知物品"
        self.level = data.get("Level")  # 品数（仅武器才有）
        """被使用的次数，次数多的优先前置"""
        self.u_popularity = data.get("u_popularity") or 0
        super().__init__()

    def __str__(self) -> str:
        x = "※" * (self.quality + 1)
        return f"{x}{self.name}({self.id}){self.bind_type_str}"

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
        return ["rgb(220,220,220)", "rgb(190,190,190)", "rgb(0, 210, 75)", "rgb(0, 126, 255)", "rgb(254, 45, 254)", "rgb(255, 165, 0)", "#ff0000"][self.quality]

    def to_row(self):
        new = [self.id, self.name, self.bind_type_str, self.html_code]
        return new

    @property
    def bind_type_str(self):
        return GoodsBindTypeBindTypes[self.bind_type.value]

    def __repr__(self) -> str:
        return json.dumps(self.__dict__)

    def to_dict(self) -> dict:
        r = copy.deepcopy(self.__dict__)
        r["img_url"] = self.img_url
        r["color"] = self.color
        r["bind_type_str"] = self.bind_type_str
        return r


class WucaiProperty:
    DICT_filter = [
        ["全身(五行石)大于等于", "个数"],
        ["(五行石)等级和大于等于", "等级"],
    ]
    DICT_value = [
        "提高"
    ]
    DICT_value_desc = {
        "内功": "内",
        "外功": "外",
        "等级": "",
        "毒性": "毒",
        "效果": "效",
        "会心": "会",
        "攻击": "攻",
        "招式产生威胁": "威胁",
        "阳性": "阳",
        "阴性": "阴",
        "混元性": "混元",
        "内破防": "内破",
        "外破防": "外破",
    }
    RE_filter_number = re.compile("\d*")

    def __init__(self, values: List[str], filters: List[str]) -> None:
        self.values = [WucaiProperty.convert_value(x) for x in values]
        self.filters = [WucaiProperty.convert_filter(x) for x in filters]

    def __str__(self) -> str:
        v = [f"{x[0]}+{x[1]}" for x in self.values]
        f = [f"{x[0]}>={x[1]}" for x in self.filters]
        r = v+f
        return str.join("\n", r)

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self):
        return copy.deepcopy(self.__dict__)

    @staticmethod
    def convert_filter(raw: str) -> Tuple[str, int]:
        """
        将条件标准化
        """
        for x in WucaiProperty.DICT_filter:
            if not raw.startswith(x[0]):
                continue
            r = raw[len(x[0]):]
            re_result = WucaiProperty.RE_filter_number.match(r)
            pos = re_result.regs[0]
            return [x[1], int(r[pos[0]: pos[1]])]
        return [f"未知:{raw}", 0]

    @staticmethod
    def convert_value(raw: str) -> Tuple[str, int]:
        """
        将属性标准化
        """
        for x in WucaiProperty.DICT_value:
            v = raw.split(x)
            if len(v) <= 1:
                continue
            re_result = WucaiProperty.RE_filter_number.match(v[1])
            pos = re_result.regs[0]
            value = WucaiProperty.convert_value_desc(v[0])
            return [value, int(v[1][pos[0]:pos[1]])]
        return [f"未知:{raw}", 0]

    @staticmethod
    def convert_value_desc(raw: str) -> str:
        d = WucaiProperty.DICT_value_desc
        for x in d:
            raw = raw.replace(x, d[x])
        return raw

    @staticmethod
    def from_html(raw_content: str) -> List[WucaiProperty]:
        """
        通过原始html转换为五彩石属性
        """
        items = get_tag_content_list(raw_content, "div")
        properties = [get_tag_content_list(x, "span") for x in items]
        result: List[WucaiProperty] = []
        for x in range(0, len(properties), 2):
            prop = [x[1] for x in properties[x:x + 2]]  # 每2个形成一对儿属性:条件
            prop_values = prop[0].split("<br>")
            prop_filters = prop[1].split("<br>")
            result.append(WucaiProperty(prop_values, prop_filters))
        return result

class GoodsInfoFull(GoodsInfo):
    def __init__(self, data: dict = None) -> None:
        super().__init__(data)
        self.typeLabel = data.get("TypeLabel")  # 分类
        self.desc = data.get("Desc")  # 描述
        self.maxDurability = data.get("MaxDurability")  # 最大耐久
        self.maxExistAmount = get_number(data.get("MaxExistAmount")) or None  # 最大拥有数
        self.attributes = json.loads(data.get("attributes") or "[]")  # 包含属性
        self.recovery_price = data.get("Price")  # 回收价
        self.level = data.get("Level")  # 品数（仅武器才有）
        data = data.get("WuCaiHtml") or ""  # 五彩石属性
        self.wucai_properties = WucaiProperty.from_html(data)  # convert to wucai-properties

    def to_dict(self) -> dict:
        r = super().to_dict()
        r["wucai_properties"] = [x.to_dict() for x in self.wucai_properties]
        return r
