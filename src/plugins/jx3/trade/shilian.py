from jinja2 import Template
from typing import Any

from src.const.path import ASSETS, build_path
from src.const.jx3.constant import server_aliases_data as servers
from src.utils.network import Request
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import SimpleHTML

from .api import template_msgbox, template_table

from ._parse import SHILIAN_ATTR_LABELS, ShilianEquipParser, coin_to_image, calculate_price, shilian_attrs_to_keys
from .local_items import search_local_shilian_equips

basic_name = "无修"

def get_exist_attrs(data: list[dict]) -> list[str]:
    attrs = []
    for item in data:
        if item.get("color") != "green":
            continue
        if item.get("key"):
            attrs.append(item["key"])
        else:
            label: str = item["label"].split("提高" if "提高" in item["label"] else "增加")[0]
            label = label.replace("等级", "").replace("值", "")
            attrs.append(label)
    return attrs


def format_attrs(data: list[dict]) -> str:
    return " ".join(
        SHILIAN_ATTR_LABELS.get(attr, attr)
        for attr in get_exist_attrs(data)
    )

async def get_equips_data(name: str, quality: int):
    return search_local_shilian_equips(name, quality, None)

async def get_equip_data(raw: str) -> Any:
    try:
        attrsInstance = ShilianEquipParser(raw)
    except ValueError as exc:
        reason = str(exc) or "词条格式有误"
        return f"无法解析试炼词条：{reason}\n请确保包含品级、内/外功、属性和部位，例如：41400外功双会招头"
    attrs, location, quality, type_ = attrsInstance.attributes, attrsInstance.location, attrsInstance.quality, attrsInstance.kungfu_type
    attr_keys = shilian_attrs_to_keys(attrs)
    if not attrs:
        return "您输入的装备词条有误，请确保包含以下四个要素：\n品级、属性、部位、内外功\n示例：13550内功双会头"
    final_name = basic_name + location + "·" + type_
    data = search_local_shilian_equips(final_name, quality, attr_keys)
    if len(data) == 0:
        return f"未查找到该{basic_name}装备！"
    else:
        for i in data:
            if set(get_exist_attrs(i["attributes"])) == set(attr_keys):
                return i
        return "不存在这样的试炼之地装备，请不要徒手造装备！"
            
async def get_wufeng_image(raw: str, server: str):
    if server == "全服":
        result = await get_wufeng_image_allserver(raw)
        return result
    data: Any = await get_equip_data(raw)
    if isinstance(data, str):
        return data
    if isinstance(data, list):
        return data[0]
    currentStatus = 0 # 当日是否具有该物品在交易行
    try:
        itemId = data["id"]
    except (KeyError, TypeError):
        return "音卡建议您不要造装备了，因为没有。"
    logs = (await Request(f"https://next2.jx3box.com/api/item-price/{itemId}/logs?server={server}").get()).json()
    current = logs["data"]["today"]
    yesterdayFlag = False
    if current is not None:
        currentStatus = 1
    else:
        if logs["data"]["yesterday"] is not None:
            yesterdayFlag = True
            currentStatus = 1
            current = logs["data"]["yesterday"]
    if current is not None:
        msgbox = Template(template_msgbox).render(
            low = coin_to_image(str(calculate_price(current["LowestPrice"]))),
            avg = coin_to_image(str(calculate_price(current["AvgPrice"]))),
            high = coin_to_image(str(calculate_price(current["HighestPrice"])))
        )
    else:
        msgbox = ""
    color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][int(data["Quality"])]
    detailData = (await Request(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server}&limit=20").get()).json()
    prices = detailData["data"]["prices"]
    if (not currentStatus or yesterdayFlag) and prices is None:
        if not yesterdayFlag:
            return "唔……该物品目前交易行没有数据。"
        else:
            if current is None:
                return "唔……该物品目前交易行没有数据。"
            low = calculate_price(current["LowestPrice"])
            avg = calculate_price(current["AvgPrice"])
            high = calculate_price(current["HighestPrice"])
            return f"唔……该物品目前交易行没有数据，但是音卡找到了昨日的数据：\n昨日低价：{low}\n昨日均价：{avg}\n昨日高价：{high}"
    if prices is None:
        return "唔……该物品目前交易行没有数据。"
    table = []
    icon = "https://icon.jx3box.com/icon/" + str(data["IconID"]) + ".png"
    name = data["Name"]
    for each_price in prices:
        table.append(
            Template(template_table).render(
                icon = icon,
                color = color,
                name = name + "<br><span style=\"color:rgb(0, 210, 75)\">" + format_attrs(data["attributes"]) + "</span>",
                time = Time(each_price["created"]).format("%m月%d日 %H:%M:%S"),
                limit = str(each_price["n_count"]),
                price = coin_to_image(calculate_price(each_price["unit_price"]))
            )
        )
        if len(table) == 12:
            break
    html = str(
        SimpleHTML(
            "jx3",
            "trade",
            font=build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
            msgbox=msgbox,
            table_content="\n".join(table),
            appinfo=f"交易行 · {server} · {name}",
            saohua="严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
        )
    )
    image = await generate(html, ".total", segment=True)
    return image

async def get_wufeng_image_allserver(raw: str):
    highs = []
    lows = []
    avgs = []
    table = []
    data: Any = await get_equip_data(raw)
    if isinstance(data, str):
        return data
    if isinstance(data, list):
        return data[0]
    currentStatus = 0 # 当日是否具有该物品在交易行
    try:
        itemId = data["id"]
    except (KeyError, TypeError):
        return "音卡建议您不要造无修装备了，因为没有。"
    for server in servers:
        logs = (await Request(f"https://next2.jx3box.com/api/item-price/{itemId}/logs?server={server}").get()).json()
        current = logs["data"]["today"]
        yesterdayFlag = False
        if current != None:
            currentStatus = 1
        else:
            if logs["data"]["yesterday"] is not None:
                yesterdayFlag = True
                currentStatus = 1
                current = logs["data"]["yesterday"]
            else:
                yesterdayFlag = 0
                currentStatus = 0
        if current is not None:
            highs.append(current["HighestPrice"])
            avgs.append(current["AvgPrice"])
            lows.append(current["LowestPrice"])
        else:
            highs.append(0)
            avgs.append(0)
            lows.append(0)
        color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][data["Quality"]]
        detailData = (await Request(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server}&limit=20").get()).json()
        icon = "https://icon.jx3box.com/icon/" + str(data["IconID"]) + ".png"
        name = data["Name"]
        prices = detailData["data"]["prices"]
        if (not currentStatus or yesterdayFlag) and prices is None:
            if not yesterdayFlag:
                # table.append(
                #     Template(template_table).render(
                #         icon = icon,
                #         color = color,
                #         name = name + f"（{server}）<br><span style=\"color:rgb(0, 210, 75)\">" + " ".join(get_exist_attrs(data["attributes"])) + "</span>",
                #         time = Time().format("%m月%d日 %H:%M:%S"),
                #         limit = "N/A",
                #         price = "<span style=\"color:red\">没有数据</span>"
                #     )
                # )
                continue
            else:
                if current is None:
                    continue
                table.append(
                    Template(template_table).render(
                        icon = icon,
                        color = color,
                        name = name + f"（{server}）<br><span style=\"color:rgb(0, 210, 75)\">" + format_attrs(data["attributes"]) + "</span>",
                        time = Time().format("%m月%d日 %H:%M:%S"),
                        limit = "N/A",
                        price = coin_to_image(calculate_price(current["AvgPrice"]))
                    )
                )
                continue
        if prices is None:
            continue
        each_price = prices[0]
        table.append(
            Template(template_table).render(
                icon = icon,
                color = color,
                name = name + f"（{server}）<br><span style=\"color:rgb(0, 210, 75)\">" + format_attrs(data["attributes"]) + "</span>",
                time = Time(each_price["created"]).format("%m月%d日 %H:%M:%S"),
                limit = str(each_price["n_count"]),
                price = coin_to_image(calculate_price(each_price["unit_price"]))
            )
        )

    fhighs = [x for x in highs if x != 0]
    favgs = [x for x in avgs if x != 0]
    flows = [x for x in lows if x != 0]
    exist_info_flag = False
    final_highest = 0
    final_avg = 0
    final_lowest = 0
    try:
        final_highest = int(sum(fhighs) / len(fhighs))
        final_avg = int(sum(favgs) / len(favgs))
        final_lowest = int(sum(flows) / len(flows))
        exist_info_flag = True
    except ZeroDivisionError:
        exist_info_flag = False
    msgbox = template_msgbox.replace("当日", "全服")
    msgbox = Template(msgbox).render(
        low = coin_to_image(calculate_price(final_lowest)) if exist_info_flag else "未知",
        avg = coin_to_image(calculate_price(final_avg)) if exist_info_flag else "未知",
        high = coin_to_image(calculate_price(final_highest)) if exist_info_flag else "未知"
    )
    if len(table) == 0:
        return "已找到该试炼之地装备，但目前全服均无报价！"
    name = data["Name"]
    html = str(
        SimpleHTML(
            "jx3",
            "trade",
            font=build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
            msgbox=msgbox,
            table_content="\n".join(table),
            appinfo=f"交易行 · 全服 · {name}",
            saohua="严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
        )
    )
    image = await generate(html, ".total", segment=True)
    return image
