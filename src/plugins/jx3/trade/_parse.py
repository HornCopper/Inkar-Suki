from typing import List

from src.const.path import ASSETS, build_path

import re

class AttrsConverter:
    def __init__(self, raw: str):
        self.raw = self._preprocess(raw)
        self._attrs = []
        self._basic_type = self._determine_basic_type()
        self._quality = self._extract_quality()
        self._location = self._determine_place()
        self._extract_attributes()

    def _preprocess(self, raw: str) -> str:
        # 去掉不必要的词汇
        raw = raw.replace("攻击", "").replace("攻", "").replace("品", "")
        return raw

    def _fd(self, keyword: str) -> bool:
        return keyword in self.raw

    def _determine_basic_type(self) -> str:
        if self._fd("外"):
            return "外功"
        elif self._fd("内"):
            return "内功"
        else:
            raise ValueError("无法确定基础攻击类型")

    def _extract_attributes(self):
        # 基础攻击
        self._attrs.append(self._basic_type + "攻击")

        # 处理属性：会心、无双、破防等
        if self._fd("纯会"):
            self._attrs.append("全会心" if self._basic_type == "内功" else self._basic_type + "会心")
        if self._fd("纯无"):
            self._attrs.append("无双")
        if self._fd("纯破"):
            self._attrs.append(self._basic_type + "破防")
        if self._fd("双会") or self._fd("会心会效") or self._fd("会会"):
            if self._basic_type == "外功":
                self._attrs.append(self._basic_type + "会心")
                self._attrs.append(self._basic_type + "会心效果")
            else:
                self._attrs.append("全会心")
                self._attrs.append("全会心效果")
        if self._fd("破") and not self._fd("纯破") and not self._fd("破招"):
            self._attrs.append(self._basic_type + "破防")
        if self._fd("招") or self._fd("破破"):
            self._attrs.append("破招")
        if self._fd("无") and not self._fd("纯无"):
            self._attrs.append("无双")
        if self._fd("会") and not any(self._fd(k) for k in ["双会", "纯会", "会效", "会心会效", "会会"]):
            self._attrs.append("全会心" if self._basic_type == "内功" else self._basic_type + "会心")

    def _extract_quality(self) -> int:
        num_list = self._extract_numbers(self.raw)
        if len(num_list) != 1:
            raise ValueError("无法确定装备品质")
        return num_list[0]

    @staticmethod
    def _extract_numbers(text: str) -> List[int]:
        return list(map(int, re.findall(r'\d+', text)))

    def _determine_place(self) -> str:
        if any(self._fd(k) for k in ["头", "帽", "脑壳"]):
            return "头饰"
        elif any(self._fd(k) for k in ["手", "臂"]):
            return "护臂"
        elif any(self._fd(k) for k in ["裤", "下装"]):
            return "裤"
        elif any(self._fd(k) for k in ["鞋", "jio", "脚"]):
            return "鞋"
        elif any(self._fd(k) for k in ["链", "项"]):
            return "项链"
        elif self._fd("腰坠") or (self._fd("坠") and not self._fd("腰带")):
            return "腰坠"
        elif any(self._fd(k) for k in ["暗器", "囊", "弓弦"]):
            return "囊"
        else:
            raise ValueError("无法确定装备部位")

    @property
    def attributes(self) -> List[str]:
        return self._attrs

    @property
    def location(self) -> str:
        return self._location

    @property
    def quality(self) -> int:
        return self._quality

def coin_to_image(rawString: str):
    brick = build_path(ASSETS, ["image", "jx3", "trade", "brick.png"])
    gold = build_path(ASSETS, ["image", "jx3", "trade", "gold.png"])
    silver = build_path(ASSETS, ["image", "jx3", "trade", "silver.png"])
    copper = build_path(ASSETS, ["image", "jx3", "trade", "copper.png"])
    to_replace = [["砖", f"<img src=\"{brick}\">"], ["金", f"<img src=\"{gold}\">"], ["银", f"<img src=\"{silver}\">"], ["铜", f"<img src=\"{copper}\">"]]
    for waiting in to_replace:
        rawString = rawString.replace(waiting[0], waiting[1])
    processedString = rawString
    return processedString

def calculator_price(price: int) -> str:
    if 1 <= price <= 99:  # 铜
        return f"{price} 铜"
    elif 100 <= price <= 9999:  # 银
        silver = price // 100
        copper = price % 100
        if copper == 0:
            return f"{silver} 银"
        else:
            return f"{silver} 银 {copper} 铜"
    elif 10000 <= price <= 99999999:  # 金
        gold = price // 10000
        silver = (price % 10000) // 100
        copper = price % 100
        result = f"{gold} 金"
        if silver:
            result += f" {silver} 银"
        if copper:
            result += f" {copper} 铜"
        return result
    elif price >= 100000000:  # 砖
        brick = price // 100000000
        gold = (price % 100000000) // 10000
        silver = (price % 10000) // 100
        copper = price % 100
        result = f"{brick} 砖"
        if gold:
            result += f" {gold} 金"
        if silver:
            result += f" {silver} 银"
        if copper:
            result += f" {copper} 铜"
        return result
    raise ValueError(f"Cannot recognize the price `{price}`!")