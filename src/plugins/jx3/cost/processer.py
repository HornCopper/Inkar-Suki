from typing import Any, Literal
from jinja2 import Template

from src.const.path import ASSETS, TEMPLATES
from src.utils.file import read
from src.utils.network import Request
from src.utils.generate import generate
from src.plugins.jx3.trade._parse import calculate_price, coin_to_image

from ._template import template_cost

async def get_item_data(name: str) -> dict[str, Any] | list[dict[str, str]] | Literal[False]:
    possible_results: list[dict[str, str]] = []
    for t in ["tailoring", "cooking", "medicine", "founding", "furniture"]:
        menu = (await Request(f"https://node.jx3box.com/manufactures?client=std&mode=simple&type={t}").get()).json()
        for i in menu:
            if i["Name"] == name:
                return (await Request(f"https://node.jx3box.com/manufacture/{t}/" + str(i["ID"]) + "?client=std").get()).json()
            if name in i["Name"]:
                possible_results.append(
                    {i["Name"]: f"https://node.jx3box.com/manufacture/{t}/" + str(i["ID"]) + "?client=std"}
                )
    if len(possible_results) == 0:
        return False
    if len(possible_results) == 1:
        return (await Request(list(possible_results[0].values())[0]).get()).json()
    else:
        return possible_results

class DataProcesser:
    coin_image = staticmethod(coin_to_image)
    calculate_price = staticmethod(calculate_price)

    def __init__(self, data: dict[str, Any]):
        self.data = data
    
    @property
    def icon(self) -> str:
        return "https://icon.jx3box.com/icon/" + str(self.data["IconID"]) + ".png"
    
    @property
    def name(self) -> str:
        return self.data["Name"]
    
    @property
    def level(self) -> int:
        return self.data["nLevel"] or 0
    
    @property
    def vigor(self) -> int:
        return self.data["CostVigor"] or 0
    
    @property
    def experience(self) -> int:
        return self.data["Exp"] or 0
    
    @property
    def output(self) -> tuple[str, float, str]: # 1 item_count 2 average count 3 item_id
        min_count = self.data["CreateItemMin1"] or 0
        max_count = self.data["CreateItemMax1"] or 0
        return str(min_count) if min_count == max_count else f"{min_count} ~ {max_count}", \
            (min_count + max_count) / 2, \
           str( self.data["CreateItemType1"]) + "_" + str(self.data["CreateItemIndex1"])

    @property
    def materials(self) -> tuple[list[str], list[int]]: # 1 item_id 2 item_count
        ids: list[str] = []
        counts: list[int] = []
        for index in range(1, 9):
            t = self.data[f"RequireItemType{index}"]
            i = self.data[f"RequireItemIndex{index}"]
            c = self.data[f"RequireItemCount{index}"]
            if isinstance(t, int) and isinstance(i, int):
                ids.append(f"{t}_{i}")
            if isinstance(c, int):
                counts.append(c)
        return ids, counts
    
    async def get_prices(self, server: str) -> tuple[dict[str, dict], list[str], list[dict[str, Any]]]: # 1 item_price 2 not in trade 3 npc trade data
        materials_id, _ = self.materials
        _, _, output_id = self.output
        all_items_id = materials_id + [output_id]
        trade_price_data: dict[str, dict[str, Any]] = (await Request("https://next2.jx3box.com/api/item-price/list?itemIds=" + ",".join(all_items_id) + f"&server={server}").get()).json()
        npc_price_data: list[dict[str, Any]] = (await Request(f"https://node.jx3box.com/craft/price?ids=" + ",".join([i.split("_")[-1] for i in materials_id]) + "&client=std").get()).json()
        trade_item_ids = list(trade_price_data["data"].keys())
        for trade_item_id in trade_item_ids:
            if trade_item_id.split("_")[-1] in [str(i["ItemIndex"]) for i in npc_price_data]:
                trade_price_data["data"].pop(trade_item_id)
        return trade_price_data["data"], [m for m in materials_id if m not in list(trade_price_data["data"].keys())], npc_price_data
    
    def get_npc_prices(self, npc_item: list[str], data: list[dict[str, Any]]) -> list[int]:
        if len(npc_item) == 0:
            return []
        ids = [i.split("_")[-1] for i in npc_item]
        results = []
        for id in ids:
            for each_item in data:
                if str(each_item["ItemIndex"]) == id:
                    results.append(
                        each_item["Price"]
                    )
                    continue
        return results
    
    async def get_materials_info(self, materials_id: list[str]) -> list[tuple[str, str]]: # list[1 icon 2 name]
        final_url = f"https://node.jx3box.com/api/node/item/search?ids=" + ",".join(materials_id) + "&page=1&per=50&client=std"
        data = (await Request(final_url).get()).json()
        results: list[tuple[str, str]] = []
        for each_id in materials_id:
            for item in data["data"]["data"]:
                if item["id"] == each_id:
                    icon = "https://icon.jx3box.com/icon/" + str(item["IconID"]) + ".png"
                    name = item["Name"]
                    results.append(
                        (icon, name)
                    )
                    continue
        return results
    
    async def render_image(self, server: str):
        materials_id, materials_count = self.materials
        all_prices, npc_item, npc_trade = await self.get_prices(server)
        count, average_count, terminal_item_id = self.output
        if terminal_item_id not in all_prices:
            terminal_item_price = {
                "HighestPrice": 0,
                "AvgPrice": 0,
                "LowestPrice": 0
            }
        else:
            terminal_item_price = all_prices[terminal_item_id]
        npc_item_price = self.get_npc_prices(npc_item, npc_trade)
        npc_item_count = []
        record_npc_item = []
        for i in range(len(materials_id)):
            for each_npc_item_id in npc_item:
                if materials_id[i].split("_")[-1] == each_npc_item_id.split("_")[-1] and each_npc_item_id not in record_npc_item:
                    npc_item_count.append(materials_count[i])
                    record_npc_item.append(each_npc_item_id)
        trade = int(terminal_item_price["AvgPrice"] * average_count)
        materials_info = await self.get_materials_info(materials_id)
        materials_table = []
        total = 0
        for each_material in materials_id:
            index = materials_id.index(each_material)
            icon, name = materials_info[index]
            require_count = materials_count[index]
            if each_material in npc_item:
                if npc_item.index(each_material) >= len(npc_item_price):
                    price = 0
                else:
                    price = npc_item_price[npc_item.index(each_material)]
            else:
                if each_material not in all_prices:
                    price = 0
                else:
                    price = all_prices[each_material]["AvgPrice"]
            total_price = price * require_count
            total += total_price
            materials_table.append(
                Template(template_cost).render(
                    icon = icon,
                    name = name,
                    count = ("(NPC)<br>" if each_material in npc_item else "(交易行)<br>") + str(require_count),
                    unit = self.coin_image(self.calculate_price(price)),
                    total = self.coin_image(self.calculate_price(total_price))
                )
            )
        html = Template(
            read(
                TEMPLATES + "/jx3/cost.html"
            )
        ).render(
            font = ASSETS + "/font/PingFangSC-Semibold.otf",
            icon = self.icon,
            name = self.name,
            level = self.level,
            vigor = self.vigor,
            experience = self.experience,
            count = count,
            highest = self.coin_image(
                self.calculate_price(
                    terminal_item_price["HighestPrice"]
                )
            ),
            average = self.coin_image(
                self.calculate_price(
                    terminal_item_price["AvgPrice"]
                )
            ),
            lowest = self.coin_image(
                self.calculate_price(
                    terminal_item_price["LowestPrice"]
                )
            ),
            cost = self.coin_image(
                self.calculate_price(
                    total
                )
            ),
            trade = self.coin_image(
                self.calculate_price(
                    trade
                )
            ),
            profit = self.coin_image(
                self.calculate_price(
                    trade - total
                )
            ),
            materials = "\n".join(materials_table),
            server = server
        )
        return await generate(html, ".container", True, segment=True)