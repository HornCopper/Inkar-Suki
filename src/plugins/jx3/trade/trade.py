from typing_extensions import Self
from datetime import datetime
from jinja2 import Template

from src.const.path import ASSETS, TEMPLATES
from src.const.jx3.server import Server
from src.utils.analyze import sort_dict_list
from src.utils.network import Request
from src.utils.file import read
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import get_saohua

from ._parse import (
    ShilianEquipParser,
    coin_to_image,
    calculate_price
)
from ._template import (
    template_v3_element,
    template_v3_price,
    template_v3_element_prefix,
    template_v3_element_shilian,
    template_v3_info,
    template_v3_log,
    template_v3_name_mulit,
    template_v3_name_one
)

import re

server_list = list(Server.server_aliases.keys())

def n2i(price: int):
    return coin_to_image(
        calculate_price(price)
    )

class JX3Item:
    def __init__(self, single_node_data: dict):
        self.data = single_node_data

    @property
    def name(self) -> str:
        return self.data["Name"]

    @property
    def icon(self) -> str:
        return "https://icon.jx3box.com/icon/" + str(self.data["IconID"]) + ".png"
    
    @property
    def effect(self) -> str:
        if self.data["Desc"] is None:
            return ""
        else:
            data = self.data["Desc"]
        decoded_data = data.encode("utf-8").decode("unicode_escape").encode("latin1").decode("utf-8").replace("\n", "")
        pattern = rf"<Text>\s*text=\"(.*?)\"\s+font={105}\s*</text>"
        match = re.search(pattern, decoded_data, re.IGNORECASE)
        result = match.group(1).strip() if match else ""
        return re.sub(r"\\+", "", result).strip()
    
    @property
    def quality(self) -> str:
        return self.data["Level"] or ""
    
    @property
    def attr(self) -> str:
        attribute = self.data["attributes"]
        if attribute == []:
            return ""
        else:
            return " ".join(
                [
                    (attr["label"].split("提高" if "提高" in attr["label"] else "增加")[0]).replace("等级", "").replace("值", "") + "(" + str(list(map(int, re.findall(r"\d+", attr["label"])))[0]) + ")"
                    for attr in self.data["attributes"]
                    if attr.get("color") == "green"
                ]
            )
        
    @property
    def peerless_effect(self) -> str:
        attribute: list[dict] = self.data["attributes"]
        if attribute == []:
            return ""
        for attr in attribute:
            if attr.get("color") == "orange":
                decoded_data = str(attr.get("label")).encode("utf-8").decode("unicode_escape").encode("latin1").decode("utf-8").replace("\n", "")
                pattern = rf"<Text>\s*text=\"(.*?)\"\s+font={101}\s*</text>"
                match = re.search(pattern, decoded_data, re.IGNORECASE)
                result = match.group(1).strip() if match else ""
                return "，".join(re.sub(r"\\+", "", result).strip()[:-1].split("。")[:-1]) + "。"
        return ""

    @property
    def color(self) -> str:
        return ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][self.data["Quality"]]
    
class ItemPriceLog:
    def __init__(self, data: list, item_id: str, server: str):
        self.data = data
        self.item_id = item_id
        self.server = server
        self.sorted_data = sort_dict_list(data, "price")[::-1]
    
    @property
    def lowest(self) -> int:
        return self.sorted_data[-1]["price"]
    
    @property
    def average(self) -> int:
        return self.sorted_data[int(len(self.sorted_data)/2)]["price"]
    
    @property
    def highest(self) -> int:
        return self.sorted_data[0]["price"]
    
class ItemPriceDetail:
    def __init__(self, data: dict):
        self.data = data

    @property
    def timestamp(self) -> int:
        return self.data["timestamp"]
    
    @property
    def count(self) -> int:
        return self.data["sample"]

    @property
    def price(self) -> int:
        return self.data["price"]

class JX3Trade:
    _node_data: list[dict] = []
    _daily_data: dict[tuple[str, str], list] = {}

    shilian_basic = "无修"

    @classmethod
    async def shilian(cls, equipment_words: str, server: str) -> Self | str:
        parser = ShilianEquipParser(equipment_words)
        attrs, location, quality, kungfu_type = parser.attributes, parser.location, parser.quality, parser.kungfu_type
        url = "https://node.jx3box.com/api/node/item/search"
        name = f"{cls.shilian_basic}{location}·{kungfu_type}·荒"
        params = {
            "keyword": name,
            "MinLevel": quality,
            "MaxLevel": quality,
            "BindType": 2,
            "client": "std"
        }
        data = (await Request(url, params=params).get()).json()
        for item in data["data"]["data"]:
            equipment_attr = set(
                    [
                        (attr["label"].split("提高" if "提高" in attr["label"] else "增加")[0]).replace("等级", "").replace("值", "")
                        for attr in item["attributes"]
                        if attr.get("color") == "green"
                    ]
                )
            if set(attrs) == equipment_attr:
                cls._node_data = data["data"]["data"]
                item_id: str = item["id"]
                return cls([item_id], server)
        return "未找到满足条件的装备，请检查该词条后重试！"
    
    @classmethod
    async def common(cls, keyword: str, server: str) -> Self | str:
        url = "https://node.jx3box.com/api/node/item/search"
        params = {
            "keyword": keyword,
            "page": 1,
            "per": 50,
            "client": "std"
        }
        data = (await Request(url, params=params).get()).json()
        if len(data["data"]["data"]) == 0:
            return "未找到相关物品，请检查后重试！"
        cls._node_data = data["data"]["data"]
        unique = False
        for each_item in cls._node_data:
            if each_item["Name"] == keyword and each_item["BindType"] in [0, 1, 2, None]:
                unique = True
                items = [each_item["id"]]
        if not unique:
            items = [i["id"] for i in data["data"]["data"] if i["BindType"] in [0, 1, 2, None]]
        items = [i for i in items if (await cls.check_trade(i, server))]
        return cls(items, server)

    def __init__(self, item_id: list[str], server: str):
        self.all_server: bool = server == "全服"
        self.item_id: list[str] = item_id
        self.server = server

        self._node_data = [i for i in self._node_data if i["BindType"] in [0, 1, 2, None]]
        self._no_data_items: list[str] = []
        self._no_data_items_muilt_server: dict[str, list] = {s: [] for s in server_list}
        self._next_log = []

    @classmethod
    async def check_trade(cls, item_id: str, server: str = "") -> bool:
        url = "https://next2.jx3box.com/api/auction/"
        if server == "全服":
            server = ""
        data: list[dict] = (await Request(url, params={"server": server or None, "item_id": item_id, "aggregate_type": "daily"}).post()).json()
        cls._daily_data[(item_id, server)] = data
        if data:
            return True
        return False

    def item_info(self, item_id: str) -> JX3Item:
        for item in self._node_data:
            if item["id"] == item_id:
                return JX3Item(item)
        raise ValueError
    
    async def get_logs(self, item_id: str, server: str) -> ItemPriceLog | None:
        if (item_id, server) in self._daily_data:
            return ItemPriceLog(self._daily_data[(item_id, server)], item_id, server)
        url = "https://next2.jx3box.com/api/auction/"
        data: list[dict] = (await Request(url, params={"server": server, "item_id": item_id, "aggregate_type": "daily"}).post()).json()
        if not data:
            if not self.all_server:
                self._no_data_items.append(item_id)
            else:
                self._no_data_items_muilt_server[server].append(item_id)
        else:
            result = ItemPriceLog(data, item_id, server)
            self._next_log.append(
                result
            )
            return result
    
    async def get_prices(self, item_id: str, server: str) -> list[ItemPriceDetail] | None:
        url = "https://next2.jx3box.com/api/auction/"
        data = (await Request(url, params={"server": server, "item_id": item_id, "aggregate_type": "hourly"}).post()).json()
        if len(data) > 20:
            data = sort_dict_list(data, "timestamp")[::-1][:20]
        return [ItemPriceDetail(i) for i in sort_dict_list(data, "price")] if data else None
    
    async def generate_image(self):
        if not self.all_server:
            [await self.get_logs(i, self.server) for i in self.item_id]
            self.item_id = [i for i in self.item_id if i not in self._no_data_items]
            if len(self.item_id) == 0:
                return "未找到相关数据！"
            elif len(self.item_id) == 1:
                unique_item_id = self.item_id[0]
                unique_item = self.item_info(unique_item_id)
                log = await self.get_logs(unique_item_id, self.server)
                if log is not None:
                    final_log = Template(template_v3_log).render(
                        lowest = n2i(log.lowest),
                        avg = n2i(log.average),
                        highest = n2i(log.highest)
                    )
                else:
                    final_log = ""
                name = Template(template_v3_name_one).render(
                    color = unique_item.color,
                    name = unique_item.name
                )
                final_prices = "\n".join(
                    [
                        Template(template_v3_price).render(
                            server = self.server,
                            name = name,
                            time = Time(p.timestamp).format(),
                            count = p.count,
                            price = n2i(p.price),
                            percent = "未知" if log is None else str(int(round(p.price / log.average, 2) * 100) - 100) + "%"
                        )
                        for p in (await self.get_prices(unique_item_id, self.server) or [])
                    ]
                )
                template_element = ""
                if unique_item.attr:
                    template_element += template_v3_element_prefix
                if unique_item.effect:
                    template_element += template_v3_element
                if unique_item.peerless_effect:
                    template_element += template_v3_element_shilian
                element = Template(template_element).render(
                    quality = unique_item.quality,
                    attr = unique_item.attr,
                    effect = unique_item.effect,
                    special = unique_item.peerless_effect
                )
                info = Template(template_v3_info).render(
                    icon = unique_item.icon,
                    color = unique_item.color,
                    name = unique_item.name,
                    element = element,
                    date = "未知" if log is None else Time(sort_dict_list(log.data, "timestamp")[-1]["timestamp"]).format(),
                )
            else:
                table = []
                for item in self.item_id:
                    item_info = self.item_info(item)
                    name = Template(template_v3_name_mulit).render(
                        icon = item_info.icon,
                        name = item_info.name,
                        color = item_info.color
                    )
                    price = await self.get_prices(item, self.server)
                    log = await self.get_logs(item, self.server) or ItemPriceLog([], "", "")
                    if price is None:
                        content = Template(template_v3_price).render(
                            server = self.server,
                            name = name,
                            time = Time(sort_dict_list(log.data, "timestamp")[-1]["timestamp"]).format(),
                            count = "0",
                            price = n2i(log.lowest),
                            percent = "0%"
                        )
                    else:
                        cheapest_price = price[0]
                        content = Template(template_v3_price).render(
                            server = self.server,
                            name = name,
                            time = Time(cheapest_price.timestamp).format(),
                            count = cheapest_price.count,
                            price = n2i(cheapest_price.price),
                            percent = "未知" if log is None else str(int(round(cheapest_price.price / log.average, 2) * 100) - 100) + "%"
                        )
                    table.append(content)
                final_log = ""
                final_prices = "\n".join(table)
                info = ""
        else:
            if len(self.item_id) > 1:
                return "该关键词已匹配到多个物品，如需使用全服交易行功能，请给出准确的物品名称！"
            unique_item_id = self.item_id[0]
            unique_item = self.item_info(unique_item_id)
            table = []
            logs: list[ItemPriceLog] = []
            for server in server_list:
                log = await self.get_logs(unique_item_id, server)
                if log is None:
                    continue
                logs.append(log)
                name = Template(template_v3_name_one).render(
                    color = unique_item.color,
                    name = unique_item.name
                )
                price = await self.get_prices(unique_item_id, server)
                if price is None:
                    content = Template(template_v3_price).render(
                        server = server,
                        name = name,
                        time = Time(sort_dict_list(log.data, "timestamp")[-1]["timestamp"]).format(),
                        count = "0",
                        price = n2i(log.lowest),
                        percent = "0%"
                    )
                else:
                    cheapest_price = price[0]
                    content = Template(template_v3_price).render(
                        server = server,
                        name = name,
                        time = Time(cheapest_price.timestamp).format(),
                        count = cheapest_price.count,
                        price = n2i(cheapest_price.price),
                        percent = "未知" if log is None else str(int(round(cheapest_price.price / log.average, 2) * 100) - 100) + "%"
                    )
                table.append(content)
            if table == []:
                return "已找到该物品，但目前全服均无价格！"
            max_price = "未知"
            avg_price = "未知"
            min_price = "未知"
            if len(logs) != 0:
                max_price = n2i(max([l.highest for l in logs]))
                avg_price = n2i(min([l.average for l in logs]))
                min_price = n2i(min([l.lowest for l in logs]))
            final_log = Template(template_v3_log).render(
                lowest = min_price,
                avg = avg_price,
                highest = max_price
            )
            final_prices = "\n".join(table)
            template_element = ""
            if unique_item.attr:
                template_element += template_v3_element_prefix
            if unique_item.effect:
                template_element += template_v3_element
            if unique_item.peerless_effect:
                template_element += template_v3_element_shilian
            element = Template(template_element).render(
                quality = unique_item.quality,
                attr = unique_item.attr,
                effect = unique_item.effect,
                special = unique_item.peerless_effect
            )
            info = Template(template_v3_info).render(
                icon = unique_item.icon,
                color = unique_item.color,
                name = unique_item.name,
                element = element,
                date = Time().format(),
            )
        final_html = Template(
            read(TEMPLATES + "/jx3/trade_v3.html")
        ).render(
            font = ASSETS + "/font/PingFangSC-Semibold.otf",
            summary = final_log,
            table = final_prices,
            info = info,
            saohua = get_saohua()
        )
        return await generate(final_html, ".container", segment=True)