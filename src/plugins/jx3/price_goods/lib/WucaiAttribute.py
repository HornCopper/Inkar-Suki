from __future__ import annotations
from src.tools.dep import *
import copy

class WucaiAttribute:
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
    RE_filter_number = re.compile("\\d*")

    def __init__(self, values: List[str], filters: List[str]) -> None:
        self.values = [WucaiAttribute.convert_value(x) for x in values]
        self.filters = [WucaiAttribute.convert_filter(x) for x in filters]

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
        for x in WucaiAttribute.DICT_filter:
            if not raw.startswith(x[0]):
                continue
            r = raw[len(x[0]):]
            re_result = WucaiAttribute.RE_filter_number.match(r)
            pos = re_result.regs[0]
            return [x[1], int(r[pos[0]: pos[1]])]
        return [f"未知:{raw}", 0]

    @staticmethod
    def convert_value(raw: str) -> Tuple[str, int]:
        """
        将属性标准化
        """
        for x in WucaiAttribute.DICT_value:
            v = raw.split(x)
            if len(v) <= 1:
                continue
            re_result = WucaiAttribute.RE_filter_number.match(v[1])
            pos = re_result.regs[0]
            value = WucaiAttribute.convert_value_desc(v[0])
            return [value, int(v[1][pos[0]:pos[1]])]
        return [f"未知:{raw}", 0]

    @staticmethod
    def convert_value_desc(raw: str) -> str:
        d = WucaiAttribute.DICT_value_desc
        for x in d:
            raw = raw.replace(x, d[x])
        return raw

    @staticmethod
    def from_html(raw_content: str) -> List[WucaiAttribute]:
        """
        通过原始html转换为五彩石属性
        """
        items = get_tag_content_list(raw_content, "div")
        properties = [get_tag_content_list(x, "span") for x in items]
        result: List[WucaiAttribute] = []
        for x in range(0, len(properties), 2):
            prop = [x[1] for x in properties[x:x + 2]]  # 每2个形成一对儿属性:条件
            prop_values = prop[0].split("<br>")
            prop_filters = prop[1].split("<br>")
            result.append(WucaiAttribute(prop_values, prop_filters))
        return result
