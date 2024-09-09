from typing import Tuple, List
from pathlib import Path

from src.tools.utils.request import get_api, post_url
from src.tools.utils.time import convert_time, get_current_time
from src.tools.generate import generate, get_uuid
from src.tools.utils.path import ASSETS, CACHE, TOOLS, VIEWS
from src.tools.utils.file import read, write
from src.tools.basic.server import Zone_mapping

import datetime
import json
import random

template_wujia = """
<tr>
    <td>$date</td>
    <td>$server</td>
    <td>$price</td>
</tr>"""

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Host": "www.aijx3.cn",
    "Origin": "https://wj.aijx3.cn",
    "Referer": "https://wj.aijx3.cn/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "wjKey": "auHxiYtcg59JEtZ5nARiX8gLPcWt2ut9"
}

aliases_map = {
    "金羁饰影礼盒": "金羁饰影三选一礼盒"
}

# 数据源和实际数据不一致 映射一次

async def queryWj(url: str, params: dict = {}):
    data = await post_url(url, headers=headers, json=params)
    return json.loads(data)

async def getRawName(alias_name: str):
    item_aliases_data = json.loads(read(TOOLS + "/item_aliases.json", "{}"))
    if alias_name in item_aliases_data:
        alias_name = item_aliases_data[alias_name]
    item_data = await queryWj("https://www.aijx3.cn/api/wj/basedata/getBaseGoodsList")
    item_data = item_data["data"]
    for each_item in item_data:
        if alias_name in each_item["goodsAliasAll"]:
            return each_item["goodsName"]
    return False

async def getItemHistory(standard_name: str) -> Tuple[List[int], List[str]]:
    current_timestamp = get_current_time()
    start_timestamp = get_current_time() - 3*30*24*60*60 # 3个月前
    data = await queryWj("https://www.aijx3.cn/api/wj/goods/getAvgGoodsPriceRecord", params={"goodsName":standard_name,"belongQf3":"", "endTime": convert_time(current_timestamp, "%Y-%m-%d"), "startTime": convert_time(start_timestamp, "%Y-%m-%d")})
    data = data["data"]
    dates = []
    prices = []
    for each_data in data:
        dates.append(convert_time(int(datetime.datetime.strptime(each_data["tradeTime"], "%Y-%m-%dT%H:%M:%S.000+0000").timestamp()), "%Y-%m-%d"))
        prices.append(each_data["price"])
    return prices[::-1], dates[::-1]

async def getItemDetail(item_name: str):
    item_data = await queryWj("https://www.aijx3.cn/api/wj/goods/getGoodsDetail", params={"goodsName": item_name})
    item_data = item_data["data"]
    if item_data == None:
        return False
    item_name = item_data["goodsName"] # 物品名称
    item_alias = item_data["goodsAlias"] # 物品别称
    publish_time = convert_time(int(datetime.datetime.strptime(item_data["publishTime"], "%Y-%m-%dT%H:%M:%S.000+0000").timestamp()), "%Y-%m-%d") # 发行时间
    publish_count_limit = item_data["publishNum"] if item_data["publishNum"] != None else "--" # 发行数量
    publish_time_limit = item_data["publishLimitTime"] if item_data["publishLimitTime"] != None else "--" # 发行时长
    binding_time_limit = item_data["limitTime"] if item_data["limitTime"] != None else "--" # 绑定时长
    raw_price = str(item_data["priceNum"]) + "元" # 发行原价
    img = item_data["imgs"][0] if item_data["imgs"] != None else "https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/Unknown.png"
    return [item_name, item_alias, publish_time, publish_count_limit, publish_time_limit, binding_time_limit, raw_price, img]
    # [物品名称, 物品别称, 发行时间, 发行数量, 发行时长, 绑定时长, 发行原价, 图片样例]

async def queryWBLInfo(item_standard_name: str):
    if item_standard_name in aliases_map:
        item_standard_name = aliases_map[item_standard_name]
    final_url = f"https://trade-api.seasunwbl.com/api/buyer/goods/list?filter[role_appearance]={item_standard_name}&filter[state]=2&goods_type=3"
    data = await get_api(final_url)
    wbl_data = []
    for each_data in data["data"]["list"][0:6]:
        server = each_data["server_name"]
        end_time = convert_time(get_current_time() + each_data["remaining_time"], "%Y-%m-%d")
        price = str(each_data["single_unit_price"] / 100) + "元"
        wbl_data.append(template_wujia.replace("$date", end_time).replace("$server", server).replace("$price", price))
    return "\n".join(wbl_data)

async def quertAJ3Info(item_standard_name: str):
    data = await queryWj("https://www.aijx3.cn/api/wj/goods/getGoodsPriceRecord", params={"goodsName":item_standard_name,"belongQf3":"","current":1,"size":100})
    full_table = {}
    zone_record_count = {
        "电信一区": 0,
        "双线一区": 0,
        "无界区": 0
    }
    for zone in [["电信一区", "电信五区", "电信八区"], ["双线一区", "双线二区", "双线四区"], ["无界区"]]:
        table = []
        for each_data in data["data"]["records"]:
            server = each_data["belongQf3"]
            if Zone_mapping(server, True) in zone:
                if zone_record_count[zone[0]] == 10:
                    continue
                end_time = convert_time(int(datetime.datetime.strptime(each_data["tradeTime"], "%Y-%m-%dT%H:%M:%S.000+0000").timestamp()), "%Y-%m-%d")
                price = str(each_data["price"]) + "元"
                table.append(template_wujia.replace("$date", end_time).replace("$server", server).replace("$price", price))
                zone_record_count[zone[0]] += 1
        full_table[zone[0]] = "\n".join(table)
    return full_table

async def getSingleItemPrice(item_name: str):
    standard_name = await getRawName(item_name)
    basic_item_info = await getItemDetail(standard_name)
    if basic_item_info == False:
        return ["唔……未收录该物品！\n请到音卡用户群内进行反馈，我们会及时添加别名！"]
    aijx3_data = await quertAJ3Info(standard_name)
    wbl_data = await queryWBLInfo(standard_name)
    html = read(VIEWS + "/jx3/trade/wujia.html")
    for each_part in aijx3_data:
        data = aijx3_data[each_part]
        if data == "":
            data = "(｡•́︿•̀｡) 该大区目前没有数据"
        html = html.replace(f"${each_part}_data", data)
    html = html.replace("$wbl_data", wbl_data)
    html = html.replace("$item_name", str(basic_item_info[0]))
    html = html.replace("$item_alias", str(basic_item_info[1]))
    html = html.replace("$publish_time", str(basic_item_info[2]))
    html = html.replace("$publish_count", str(basic_item_info[3]))
    html = html.replace("$publish_remain", str(basic_item_info[4]))
    html = html.replace("$binding_time", str(basic_item_info[5]))
    html = html.replace("$publish_price", str(basic_item_info[6]))
    html = html.replace("$item_image", str(basic_item_info[7]))
    prices, dates = await getItemHistory(standard_name)
    html = html.replace("$dates", json.dumps(dates, ensure_ascii=False))
    html = html.replace("$values", json.dumps(prices, ensure_ascii=False))
    font = ASSETS + "/font/custom.ttf"
    random_background = ASSETS + "/image/assistance/" + str(random.randint(1, 10)) + ".jpg"
    custom_msg = await get_api("https://inkar-suki.codethink.cn/ajs_lu")
    msg = custom_msg["msg"]
    html = html.replace(f"$customfont", font).replace("$custombackground", random_background).replace("$custom_msg", msg)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "body", False)
    return Path(final_path).as_uri()