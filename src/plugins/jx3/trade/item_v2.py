from typing import Tuple, List, Literal
from pathlib import Path
from jinja2 import Template

from src.const.jx3.server import Server
from src.const.path import ASSETS, TEMPLATES, build_path
from src.utils.network import Request
from src.utils.time import Time
from src.utils.file import read
from src.utils.generate import generate

from ._template import headers, template_wujia

import datetime
import json

async def query_aijx3_data(url: str, params: dict = {}):
    data = (await Request(url, headers=headers, params=params).post()).json()
    return data

async def get_standard_name(alias_name: str) -> str | list:
    item_data = await query_aijx3_data("https://www.aijx3.cn/api/wj/basedata/getBaseGoodsList")
    item_data = item_data["data"]
    
    # 精准匹配 如果成功匹配不再模糊搜索
    for each_item in item_data:
        if alias_name in each_item["goodsAliasAll"] or alias_name == each_item["goodsName"]:
            return each_item["goodsName"]
    
    # 模糊搜索 给出列表
    matched = []
    for each_item in item_data:
        aliases = each_item["goodsAliasAll"]
        for alias in aliases:
            if alias_name in alias:
                matched.append(each_item["goodsName"])
    return matched

async def get_item_history(standard_name: str) -> Tuple[List[int], List[str]]:
    current_timestamp = Time().raw_time
    start_timestamp = current_timestamp - 3*30*24*60*60 # 3个月前
    params = {
        "goodsName":standard_name,
        "belongQf3":"", 
        "endTime": Time(current_timestamp).format("%Y-%m-%d"), 
        "startTime": Time(start_timestamp).format("%Y-%m-%d")
    }
    data = await query_aijx3_data("https://www.aijx3.cn/api/wj/goods/getAvgGoodsPriceRecord", params=params)
    data = data["data"]
    dates = []
    prices = []
    for each_data in data:
        dates.append(
            Time(
                int(
                    datetime.datetime.strptime(
                        each_data["tradeTime"], "%Y-%m-%dT%H:%M:%S.000+0000"
                    ).timestamp()
                )
            ).format(
                "%Y-%m-%d"
                )
            )
        prices.append(each_data["price"])
    return prices[::-1], dates[::-1]

async def get_item_detail(item_name: str) -> list | Literal[False]:
    item_data = await query_aijx3_data("https://www.aijx3.cn/api/wj/goods/getGoodsDetail", params={"goodsName": item_name})
    item_data = item_data["data"]
    if item_data is None:
        return False
    item_name = item_data["goodsName"]
    item_alias = item_data["goodsAlias"]
    publish_time = Time(int(datetime.datetime.strptime(item_data["publishTime"], "%Y-%m-%dT%H:%M:%S.000+0000").timestamp())).format("%Y-%m-%d") # 发行时间
    publish_count_limit = item_data["publishNum"] if item_data["publishNum"] != None else "--" # 发行数量
    publish_time_limit = item_data["publishLimitTime"] if item_data["publishLimitTime"] != None else "--" # 发行时长
    binding_time_limit = item_data["limitTime"] if item_data["limitTime"] != None else "--" # 绑定时长
    raw_price = str(item_data["priceNum"]) + "元" # 发行原价
    img = item_data["imgs"][0] if item_data["imgs"] != None else "https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/Unknown.png"
    return [item_name, item_alias, publish_time, publish_count_limit, publish_time_limit, binding_time_limit, raw_price, img]
    # [物品名称, 物品别称, 发行时间, 发行数量, 发行时长, 绑定时长, 发行原价, 图片样例]

async def get_wanbaolou_data(item_standard_name: str):
    final_url = f"https://trade-api.seasunwbl.com/api/buyer/goods/list?filter[role_appearance]={item_standard_name}&filter[state]=2&goods_type=3"
    data = (await Request(final_url).get()).json()
    if data["code"] == -11:
        return "万宝楼正在维护中……暂时没有数据"
    wbl_data = []
    for each_data in data["data"]["list"][0:6]:
        server = each_data["server_name"]
        end_time = Time(Time().raw_time + each_data["remaining_time"]).format("%Y-%m-%d")
        price = str(each_data["single_unit_price"] / 100) + "元"
        wbl_data.append(
            Template(template_wujia).render(
                date = end_time,
                server = server,
                price = price
            )
        )
    return "\n".join(wbl_data)

async def get_item_price(item_standard_name: str):
    data = await query_aijx3_data("https://www.aijx3.cn/api/wj/goods/getGoodsPriceRecord", params={"goodsName":item_standard_name,"belongQf3":"","current":1,"size":100})
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
            if Server(server).zone_legacy in zone:
                if zone_record_count[zone[0]] == 10:
                    continue
                end_time = Time(int(datetime.datetime.strptime(each_data["tradeTime"], "%Y-%m-%dT%H:%M:%S.000+0000").timestamp())).format("%Y-%m-%d")
                price = str(each_data["price"]) + "元"
                table.append(
                    Template(template_wujia).render(
                        date = end_time,
                        server = server,
                        price = price
                    )
                )
                zone_record_count[zone[0]] += 1
        full_table[zone[0]] = "\n".join(table)
    return full_table

def select_min_max(data: list, margin: float = 0.1, round_to: int = 10) -> tuple[int, int]:
    if not data:
        return 0, 100000
    data = [float(item) for item in data]
    data_min = min(data)
    data_max = max(data)
    data_range = data_max - data_min
    extend = data_range * margin
    optimal_min = data_min - extend
    optimal_max = data_max + extend
    def round_down(value: float, round_to: int) -> float:
        return (value // round_to) * round_to
    def round_up(value: float, round_to: int) -> float:
        return ((value + round_to - 1) // round_to) * round_to
    adjusted_min = round_down(optimal_min, round_to)
    adjusted_max = round_up(optimal_max, round_to)
    return int(adjusted_min), int(adjusted_max)

async def get_single_item_price(item_name: str, exact: bool = False) -> str | dict | list | None:
    standard_name = await get_standard_name(item_name)
    if isinstance(standard_name, list):
        return {"v": standard_name}
    if exact:
        standard_name = item_name
    basic_item_info = await get_item_detail(standard_name)
    if basic_item_info == False:
        return ["唔……未收录该物品！\n请到音卡用户群内进行反馈，我们会及时添加别名！"]
    aijx3_data = await get_item_price(standard_name)
    wbl_data = await get_wanbaolou_data(standard_name)
    prices, dates = await get_item_history(standard_name)
    max, min = select_min_max(prices)
    html = Template(read(build_path(TEMPLATES, ["jx3", "item_price.html"]))).render(
        font = build_path(ASSETS, ["font", "custom.ttf"]),
        item_image = str(basic_item_info[7]),
        item_name = str(basic_item_info[0]),
        item_alias = str(str(basic_item_info[1])),
        custom_msg = (await Request("https://inkar-suki.codethink.cn/ajs_lu").get()).json()["msg"],
        publish_time = str(basic_item_info[2]),
        publish_count = str(basic_item_info[3]),
        publish_remain = str(basic_item_info[4]),
        binding_time = str(basic_item_info[5]),
        publish_price = str(basic_item_info[6]),
        aijx3_data = aijx3_data,
        wanbaolou = wbl_data,
        dates = json.dumps(dates, ensure_ascii=False),
        max = max,
        min = min,
        values = json.dumps(prices, ensure_ascii=False)
    )
    final_path = await generate(html, "body", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()