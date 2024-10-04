from pathlib import Path
from typing import List
from jinja2 import Template

from nonebot.adapters.onebot.v11 import MessageSegment as ms

from src.const.path import ASSETS, build_path
from src.const.jx3.constant import server_aliases_data as servers
from src.utils.analyze import check_number, extract_numbers
from src.utils.network import Request
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import SimpleHTML

from .api import template_msgbox, template_table

from ._parse import AttrsConverter, coin_to_image, calculator_price

import json
basic_name = "无封"

def get_exist_attrs(data: List[dict]) -> List[str]:
    attrs = []
    for item in data:
        if item.get("color") == "green":
            label: str = item["label"].split("提高" if "提高" in item["label"] else "增加")[0]
            label = label.replace("等级", "").replace("值", "")
            attrs.append(label)
    return attrs

async def get_equips_data(name: str, quality: int):
    url = f"https://node.jx3box.com/api/node/item/search?ids=&keyword={name}&client=std&MinLevel={quality}&MaxLevel={quality}&BindType=2"
    satisfied = []
    data = (await Request(url).get()).json()
    for x in data["data"]["data"]:
        if str(x["Level"]) == str(quality):
            satisfied.append(x)
    return satisfied

async def get_equip_data(raw: str):
    attrsInstance = AttrsConverter(raw)
    attrs, location, quality = attrsInstance.attributes, attrsInstance.location, attrsInstance.quality
    if not attrs:
        return [f"您输入的装备词条有误，请确保包含以下四个要素：\n品级、属性、部位、内外功\n示例：13550内功双会头"]
    final_name = basic_name + location
    data = await get_equips_data(final_name, quality)
    if len(data) == 0:
        return [f"未查找到该{basic_name}装备！"]
    else:
        for i in data:
            if set(get_exist_attrs(i["attributes"])) == set(attrs):
                return i
        raise ValueError
            
async def get_wufeng_image(raw: str, server: str):
    if server == "全服":
        result = await get_wufeng_image_allserver(raw)
        return result
    data = await get_equip_data(raw)
    if isinstance(data, list):
        return data
    currentStatus = 0 # 当日是否具有该物品在交易行
    try:
        itemId = data["id"]
    except:
        emg = (await Request("https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/emoji.jpg").get()).content
        return ["音卡建议您不要造无封装备了，因为没有。\n" + ms.image(emg)]
    logs = (await Request(f"https://next2.jx3box.com/api/item-price/{itemId}/logs?server={server}").get()).json()
    current = logs["data"]["today"]
    yesterdayFlag = False
    if current != None:
        currentStatus = 1
    else:
        if logs["data"]["yesterday"] != None:
            yesterdayFlag = True
            currentStatus = 1
            current = logs["data"]["yesterday"]
    if currentStatus:
        msgbox = Template(template_msgbox).render(
            low = coin_to_image(str(calculator_price(current["LowestPrice"]))),
            avg = coin_to_image(str(calculator_price(current["AvgPrice"]))),
            high = coin_to_image(str(calculator_price(current["HighestPrice"])))
        )
    else:
        msgbox = ""
    color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][data["Quality"]]
    detailData = (await Request(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server}&limit=20").get()).json()
    if (not currentStatus or yesterdayFlag) and detailData["data"]["prices"] is None:
        if not yesterdayFlag:
            return ["唔……该物品目前交易行没有数据。"]
        else:
            low = calculator_price(current["LowestPrice"])
            avg = calculator_price(current["AvgPrice"])
            high = calculator_price(current["HighestPrice"])
            return [f"唔……该物品目前交易行没有数据，但是音卡找到了昨日的数据：\n昨日低价：{low}\n昨日均价：{avg}\n昨日高价：{high}"]
    table = []
    icon = "https://icon.jx3box.com/icon/" + str(data["IconID"]) + ".png"
    name = data["Name"]
    for each_price in detailData["data"]["prices"]:
        table.append(
            Template(template_table).render(
                icon = icon,
                color = color,
                name = name + "<br><span style=\"color:rgb(0, 210, 75)\">" + " ".join(get_exist_attrs(data["attributes"])) + "</span>",
                time = Time(each_price["created"]).format("%m月%d日 %H:%M:%S"),
                limit = str(each_price["n_count"]),
                price = coin_to_image(calculator_price(each_price["unit_price"]))
            )
        )
        if len(table) == 12:
            break
    html = str(
        SimpleHTML(
            "jx3",
            "trade",
            font=build_path(ASSETS, ["font", "custom.ttf"]),
            msgbox=msgbox,
            table_content="\n".join(table),
            appinfo=f"交易行 · {server} · {name}",
            saohua="严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
        )
    )
    final_path = await generate(html, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()

async def get_wufeng_image_allserver(raw: str):
    highs = []
    lows = []
    avgs = []
    table = []
    data = await get_equip_data(raw)
    if isinstance(data, list):
        return data
    currentStatus = 0 # 当日是否具有该物品在交易行
    try:
        itemId = data["id"]
    except KeyError:
        emg = (await Request("https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/emoji.jpg").get()).content
        return ["音卡建议您不要造无封装备了，因为没有。\n" + ms.image(emg)]
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
        if currentStatus:
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
        if (not currentStatus or yesterdayFlag) and detailData["data"]["prices"] is None:
            if not yesterdayFlag:
                table.append(
                    Template(template_table).render(
                        icon = icon,
                        color = color,
                        name = name + f"（{server}）<br><span style=\"color:rgb(0, 210, 75)\">" + " ".join(get_exist_attrs(data["attributes"])) + "</span>",
                        time = Time().format("%m月%d日 %H:%M:%S"),
                        limit = "N/A",
                        price = "<span style=\"color:red\">没有数据</span>"
                    )
                )
                continue
            else:
                table.append(
                    Template(template_table).render(
                        icon = icon,
                        color = color,
                        name = name + f"（{server}）<br><span style=\"color:rgb(0, 210, 75)\">" + " ".join(get_exist_attrs(data["attributes"])) + "</span>",
                        time = Time().format("%m月%d日 %H:%M:%S"),
                        limit = "N/A",
                        price = coin_to_image(calculator_price(current["AvgPrice"]))
                    )
                )
                continue
        each_price = detailData["data"]["prices"][0]
        table.append(
            Template(template_table).render(
                icon = icon,
                color = color,
                name = name + f"（{server}）<br><span style=\"color:rgb(0, 210, 75)\">" + " ".join(get_exist_attrs(data["attributes"])) + "</span>",
                time = Time(each_price["created"]).format("%m月%d日 %H:%M:%S"),
                limit = str(each_price["n_count"]),
                price = coin_to_image(calculator_price(each_price["unit_price"]))
            )
        )

    fhighs = [x for x in highs if x != 0]
    favgs = [x for x in avgs if x != 0]
    flows = [x for x in lows if x != 0]
    exist_info_flag = False
    try:
        final_highest = int(sum(fhighs) / len(fhighs))
        final_avg = int(sum(favgs) / len(favgs))
        final_lowest = int(sum(flows) / len(flows))
        exist_info_flag = True
    except:
        pass
    msgbox = template_msgbox.replace("当日", "全服")
    msgbox = Template(msgbox).render(
        low = coin_to_image(calculator_price(final_lowest)) if exist_info_flag else "未知",
        avg = coin_to_image(calculator_price(final_avg)) if exist_info_flag else "未知",
        high = coin_to_image(calculator_price(final_highest)) if exist_info_flag else "未知"
    )
    html = str(
        SimpleHTML(
            "jx3",
            "trade",
            font=build_path(ASSETS, ["font", "custom.ttf"]),
            msgbox=msgbox,
            table_content="\n".join(table),
            appinfo=f"交易行 · {server} · {name}",
            saohua="严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
        )
    )
    final_path = await generate(html, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()