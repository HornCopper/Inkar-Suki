from pathlib import Path
from jinja2 import Template

from src.const.path import ASSETS, build_path
from src.const.jx3.constant import server_aliases_data as servers
from src.utils.analyze import check_number
from src.utils.network import Request
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import SimpleHTML

from ._parse import coin_to_image, calculator_price
from ._template import template_msgbox, template_table

import datetime

filters = ["无封","无皇","封头","封护","封裤","封项","封鞋","封囊"]
banned = ["囊","头饰","裤","护臂","腰坠","项链","鞋"]

async def get_trade_image(server: str, name: str, items: list = []):
    if server == "全服":
        data = await get_trade_image_allserver(name)
        return data
    for i in filters:
        if name.find(i) != -1:
            return ["唔……请勿查找无封装备！\n如果您需要查找无封装备，可以使用“交易行无封”（注意没有空格），使用方法参考：交易行无封 服务器 词条\n词条示例：13550内功双会头"]
    for i in banned:
        if name == i:
            return ["唔……请勿查找无封装备！"]
    final_list = []
    if items == []:
        itemData = (await Request(f"https://node.jx3box.com/api/node/item/search?ids=&keyword={name}&client=std&per=35").get()).json()
        if itemData["data"]["total"] == 0:
            return ["唔……您搜索的物品尚未收录！"]
        final_list = itemData["data"]["data"]
    else:
        for i in items:
            itemData = (await Request(f"https://node.jx3box.com/api/node/item/search?ids=&keyword={i}&client=std&per=5").get()).json()
            if itemData["data"]["total"] == 0:
                continue
            else:
                for x in itemData["data"]["data"]:
                    final_list.append(x)
    itemList_searchable = []
    for i in final_list:
        new = {}
        if i["BindType"] not in [0, 1, 2, None]:
            continue
        id = i["id"]
        itemAPIData = (await Request(f"https://next2.jx3box.com/api/item-price/{id}/logs?server={server}&limit=20").get()).json()
        if itemAPIData["data"]["logs"] is None:
            continue
        else:
            new["data"] = itemAPIData["data"]
        new["id"] = str(id)
        new["icon"] = f"https://icon.jx3box.com/icon/" + str(i["IconID"]) + ".png"
        new["name"] = i["Name"]
        new["quality"] = i["Quality"] if check_number(i["Quality"]) else 0
        itemList_searchable.append(new)
    if len(itemList_searchable) == 1:
        currentStatus = 0 # 当日是否具有该物品在交易行
        yesterdayFlag = False
        current = itemList_searchable[0]["data"]["today"]
        if current != None:
            currentStatus = 1
        else:
            if itemList_searchable[0]["data"]["yesterday"] != None:
                yesterdayFlag = True
                currentStatus = 1
                current = itemList_searchable[0]["data"]["yesterday"]
        if currentStatus:
            msgbox = Template(template_msgbox).render(
                low=coin_to_image(str(calculator_price(current["LowestPrice"]))),
                avg=coin_to_image(str(calculator_price(current["AvgPrice"]))),
                high=coin_to_image(str(calculator_price(current["HighestPrice"])))
            )
        else:
            msgbox = ""
        color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][itemList_searchable[0]["quality"]]
        itemId = itemList_searchable[0]["id"]
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
        for each_price in detailData["data"]["prices"]:
            table_content = Template(template_table).render(
                icon=itemList_searchable[0]["icon"],
                color=color,
                name=itemList_searchable[0]["name"],
                time=Time(each_price["created"]).format("%m月%d日 %H:%M:%S"),
                limit=str(each_price["n_count"]),
                price=coin_to_image(str(calculator_price(each_price["unit_price"])))
            )
            table.append(table_content)
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
    else:
        # 如果有多个，则分别显示近期价格，只显示最新一条
        table = []
        for each_item in itemList_searchable:
            color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][each_item["quality"]]
            itemId = each_item["id"]
            final_name = each_item["name"]
            itemData = (await Request(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server}&limit=20").get()).json()
            table_content = template_table
            if itemData["data"]["prices"] is None:
                # 转用已存储的Log进行处理
                itemData = each_item["data"]["logs"][-1]
                time_that = itemData["CreatedAt"]
                timestamp = datetime.datetime.strptime(time_that, "%Y-%m-%dT%H:%M:%S+08:00")
                final_time = str(Time(int(timestamp.timestamp())).format("%m月%d日 %H:%M:%S"))
                count = str(itemData["SampleSize"])
                table.append(
                    Template(template_table).render(
                        icon=each_item["icon"],
                        color=color,
                        name=final_name,
                        time=final_time,
                        limit=count,
                        price=coin_to_image(str(calculator_price(itemData["AvgPrice"])))
                    )
                )
            else:
                # 使用最新一条数据
                itemData = itemData["data"]["prices"][0]
                final_time = str(Time(itemData["created"]).format("%m月%d日 %H:%M:%S"))
                count = str(itemData["n_count"])
                table.append(
                    Template(template_table).render(
                        icon=each_item["icon"],
                        color=color,
                        name=final_name,
                        time=final_time,
                        limit=count,
                        price=coin_to_image(str(calculator_price(itemData["unit_price"])))
                    )
                )
        html = str(
            SimpleHTML(
                "jx3",
                "trade",
                font = build_path(ASSETS, ["font", "custom.ttf"]),
                msgbox = "",
                table_content = "\n".join(table),
                appinfo = f"交易行 · {server} · {name}",
                saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
            )
        )
        final_path = await generate(html, ".total", False)
        if not isinstance(final_path, str):
            return
        return Path(final_path).as_uri()

async def get_trade_image_allserver(name: str):
    table = []
    lows = []
    avgs = []
    highs = []
    for i in filters:
        if name.find(i) != -1:
            return ["唔……请勿查找无封装备！\n如果您需要查找无封装备，可以使用“交易行无封”（注意没有空格），使用方法参考：交易行无封 服务器 词条\n词条示例：13550内功双会头"]
    for i in banned:
        if name == i:
            return ["唔……请勿查找无封装备！"]
    final_list = []
    itemData = (await Request(f"https://node.jx3box.com/api/node/item/search?ids=&keyword={name}&client=std&per=35").get()).json()
    if itemData["data"]["total"] == 0:
        return ["唔……您搜索的物品尚未收录！"]
    final_list = itemData["data"]["data"]
    for server in servers:
        itemList_searchable = []
        for i in final_list:
            new = {}
            if i["BindType"] not in [0, 1, 2, None]:
                continue
            id = i["id"]
            itemAPIData = (await Request(f"https://next2.jx3box.com/api/item-price/{id}/logs?server={server}&limit=20").get()).json()
            new["data"] = itemAPIData["data"]
            new["id"] = str(id)
            new["icon"] = f"https://icon.jx3box.com/icon/" + str(i["IconID"]) + ".png"
            new["name"] = i["Name"]
            new["quality"] = i["Quality"] if check_number(i["Quality"]) else 0
            itemList_searchable.append(new)
        if len(itemList_searchable) == 1:
            currentStatus = 0 # 当日是否具有该物品在交易行
            yesterdayFlag = False
            current = itemList_searchable[0]["data"]["today"]
            if current != None:
                currentStatus = 1
            else:
                if itemList_searchable[0]["data"]["yesterday"]  != None:
                    yesterdayFlag = True
                    currentStatus = 1
                    current = itemList_searchable[0]["data"]["yesterday"] 
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
            color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][itemList_searchable[0]["quality"]]
            itemId = itemList_searchable[0]["id"]
            icon = itemList_searchable[0]["icon"]
            detailData = (await Request(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server}&limit=20").get()).json()
            if (not currentStatus or yesterdayFlag) and detailData["data"]["prices"] is None:
                if not yesterdayFlag:
                    table.append(Template(template_table).render(
                            icon=icon,
                            color=color,
                            name=f"{name}（{server}）",
                            time=Time().format("%m月%d日 %H:%M:%S"),
                            limit="N/A",
                            price="<span style=\"color:red\">没有数据</span>"
                        )
                    )
                    continue
                else:
                    table.append(Template(template_table).render(
                            icon=icon,
                            color=color,
                            name=f"{name}（{server}）",
                            time=Time().format("%m月%d日 %H:%M:%S"),
                            limit="N/A",
                            price=coin_to_image(str(calculator_price(current["AvgPrice"])))
                        )
                    )
                    continue
            table.append(Template(template_table).render(
                    icon=itemList_searchable[0]["icon"],
                    color=color,
                    name=itemList_searchable[0]["name"] + f"（{server}）",
                    time=Time().format("%m月%d日 %H:%M:%S"),
                    limit=str(detailData["data"]["prices"][0]["n_count"]),
                    price=coin_to_image(str(calculator_price(detailData["data"]["prices"][0]["unit_price"])))
                )
            )
        else:
            return ["唔……您给出的物品名称似乎不够精准，全服交易行价格查询最好给出准确名称哦！"]
    fhighs = [x for x in highs if x != 0]
    favgs = [x for x in avgs if x != 0]
    flows = [x for x in lows if x != 0]
    try:
        final_highest = int(sum(fhighs) / len(fhighs))
        final_avg = int(sum(favgs) / len(favgs))
        final_lowest = int(sum(flows) / len(flows))
    except:
        return ["唔……该物品全服均没有数据！"]
    msgbox = Template(template_msgbox).render(
        low=coin_to_image(str(calculator_price(final_lowest))),
        avg=coin_to_image(str(calculator_price(final_avg))),
        high=coin_to_image(str(calculator_price(final_highest)))
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