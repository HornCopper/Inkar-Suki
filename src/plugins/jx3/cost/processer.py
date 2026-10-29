from typing import Any, Literal
from jinja2 import Template
from pydantic import BaseModel

from src.const.path import ASSETS, TEMPLATES
from src.utils.analyze import sort_dict_list
from src.utils.file import read
from src.utils.network import Request
from src.utils.jx3_data import get_item, npc_price, search_recipes
from src.utils.generate import generate
from src.plugins.jx3.trade.parsers import calculate_price, coin_to_image

from ._template import template_cost

import re

async def get_item_data(name: str) -> dict[str, Any] | list[dict[str, str]] | Literal[False]:
    matches = search_recipes(name)
    if not matches:
        return False
    if len(matches) == 1:
        return matches[0]
    return [{row["Name"]: row["key"]} for row in matches[:20]]

class Material(BaseModel):
    item_type: int
    item_index: int
    count: int

class JX3CostCalc:
    coin_image = staticmethod(coin_to_image)
    calculate_price = staticmethod(calculate_price)

    def __init__(self, data: dict[str, Any], server: str):
        self.name = data["Name"]
        self.raw_data = data
        self.npc_price: dict[str, int] = {}
        self.trade_price: dict[str, int] = {}

        self.server = server
        self.item_id = str(data["CreateItemType1"]) + "_" + str(data["CreateItemIndex1"])

    @property
    def icon(self) -> str:
        return "https://icon.jx3box.com/icon/" + str(self.raw_data["IconID"]) + ".png"

    @property
    def level(self) -> int:
        return self.raw_data["nLevel"] or 0

    @property
    def vigor(self) -> int:
        return self.raw_data["CostVigor"] or 0

    @property
    def experience(self) -> int:
        return self.raw_data["Exp"] or 0

    @property
    def tip(self) -> str:
        tip = self.raw_data["szTip"]
        if tip is None:
            return ""
        if not tip:
            return ""
        else:
            data = tip
            decoded_data = data.replace("\\n", "").replace("\n", "")
            pattern = rf"<Text>\s*text=\"(.*?)\"\s+font={18}\s*</text>"
            match = re.search(pattern, decoded_data, re.IGNORECASE)
            result = match.group(1).strip() if match else ""
            return " | " + re.sub(r"\\+", "", result).strip()

    @property
    def output(self) -> str:
        min_count = self.raw_data["CreateItemMin1"] or 0
        max_count = self.raw_data["CreateItemMax1"] or 0
        return str(min_count) if min_count == max_count else f"{min_count} ~ {max_count}"

    @property
    def avg_output(self) -> float:
        min_count = self.raw_data["CreateItemMin1"] or 0
        max_count = self.raw_data["CreateItemMax1"] or 0
        return (min_count + max_count) / 2

    @property
    def materials(self) -> list[Material]:
        results: list[Material] = []
        for index in range(1, 9):
            if not self.raw_data.get(f"RequireItemType{index}") or not self.raw_data.get(f"RequireItemIndex{index}"):
                continue
            results.append(
                Material(
                    item_type = self.raw_data[f"RequireItemType{index}"],
                    item_index = self.raw_data[f"RequireItemIndex{index}"],
                    count = self.raw_data[f"RequireItemCount{index}"],
                ),
            )
        return results

    async def get_craft_price(self):
        """
        获取NPC出售的物品。
        """
        for material in self.materials:
            key = f"{material.item_type}_{material.item_index}"
            price = npc_price(key)
            if price is not None:
                self.npc_price[key] = price

    @staticmethod
    async def get_trade_price(item_id: str, server: str) -> int:
        url = "https://next2.jx3box.com/api/auction/"
        data = (
            await Request(
                url,
                params = {
                    "server": server,
                    "item_id": item_id,
                    "aggregate_type": "hourly",
                },
            ).post()
        ).json()
        if not data:
            data = (
                await Request(
                    url,
                    params = {
                        "server": server,
                        "item_id": item_id,
                        "aggregate_type": "daily",
                    },
                ).post()
            ).json()
            if not data:
                return 0
        return sort_dict_list(data, "timestamp")[::-1][0]["price"]

    async def get_last_price(self):
        """
        获取剩余物品。
        """
        materials = [m for m in self.materials if f"{m.item_type}_{m.item_index}" not in self.npc_price]
        for m in materials:
            price = await self.get_trade_price(f"{m.item_type}_{m.item_index}", self.server)
            self.trade_price[f"{m.item_type}_{m.item_index}"] = price

    async def get_30d_price(self) -> tuple[int, int, int]:
        """
        获取30日价格。
        """
        url = "https://next2.jx3box.com/api/auction/"
        data: list[dict] = (
            await Request(
                url,
                params = {
                    "server": self.server,
                    "item_id": self.item_id,
                    "aggregate_type": "daily",
                },
            ).post()
        ).json()
        data = sort_dict_list(data, "timestamp")[::-1]
        if not data:
            return (0, 0, 0)
        return (data[0]["price"], data[int(len(data) / 2)]["price"], data[-1]["price"])

    async def get_materials_info(self, materials_id: list[str]) -> dict[str, tuple[str, str]]:
        results = {}
        for each_id in materials_id:
            item = get_item(each_id)
            if item is None:
                raise ValueError(f"本地物品资料缺失：{each_id}")
            results[each_id] = (item["Icon"]["FileName"], item["Name"])
        return results

    async def render_image(self):
        materials = self.materials
        await self.get_craft_price()
        await self.get_last_price()
        materials_info = await self.get_materials_info([f"{m.item_type}_{m.item_index}" for m in materials], )
        materials_table = []
        total = 0
        for each_material in materials:
            item_id = f"{each_material.item_type}_{each_material.item_index}"
            icon, name = materials_info[item_id]
            require_count = each_material.count
            item_type = "npc" if item_id in self.npc_price else "trade"
            price = (self.npc_price if item_type == "npc" else self.trade_price)[item_id]
            total_price = price * require_count
            total += total_price
            materials_table.append(
                Template(template_cost).render(
                    icon = icon,
                    name = name,
                    count = ("(NPC)<br>" if item_type == "npc" else "(交易行)<br>") + str(require_count),
                    unit = self.coin_image(self.calculate_price(price)),
                    total = self.coin_image(self.calculate_price(total_price)),
                ),
            )
        highest, average, lowest = await self.get_30d_price()
        item_latest_price = await self.get_trade_price(self.item_id, self.server)
        trade = self.avg_output * item_latest_price
        html = Template(read(TEMPLATES + "/jx3/cost.html")).render(
            tip = self.tip,
            font = ASSETS + "/font/PingFangSC-Semibold.otf",
            icon = self.icon,
            name = self.name,
            level = self.level,
            vigor = self.vigor,
            experience = self.experience,
            count = self.output,
            highest = self.coin_image(
                self.calculate_price(highest),
            ),
            average = self.coin_image(
                self.calculate_price(average),
            ),
            lowest = self.coin_image(
                self.calculate_price(lowest),
            ),
            cost = self.coin_image(self.calculate_price(total)),
            trade = self.coin_image(self.calculate_price(int(trade * 0.95))),
            profit = self.coin_image(self.calculate_price(int(trade * 0.95) - total)),
            materials = "\n".join(materials_table),
            server = self.server,
        )
        return await generate(html, ".container", True, segment = True)
