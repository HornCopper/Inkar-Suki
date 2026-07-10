from collections import defaultdict
from pathlib import Path
from typing import Any

from jinja2 import Template

from src.config import Config
from src.const.path import ASSETS, TEMPLATES, build_path
from src.utils.database import db
from src.utils.database.classes import ItemKeywordMap
from src.utils.file import read
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.time import Time

from ._template import template_wujia

import json


def _format_price(value: Any) -> str:
    try:
        price = float(value)
    except (TypeError, ValueError):
        return "--"
    return f"{price:g}元"


def get_item_price(item_data: dict) -> dict[str, str]:
    tables = {"电信一区": "", "双线一区": "", "无界区": ""}
    grouped_records = {"电信一区": [], "双线一区": [], "无界区": []}
    records = []
    for group in item_data.get("list") or []:
        if not isinstance(group, list):
            continue
        records.extend(
            record
            for record in group
            if isinstance(record, dict) and record.get("source") != 4
        )
    records = sorted(records, key=lambda record: record.get("date") or "", reverse=True)

    for record in records:
        zone = str(record.get("zone") or "")
        if zone.startswith("电信"):
            grouped_records["电信一区"].append(record)
        elif zone.startswith("双线"):
            grouped_records["双线一区"].append(record)
        elif zone.startswith("无界"):
            grouped_records["无界区"].append(record)

    for zone, zone_records in grouped_records.items():
        rows = []
        for record in zone_records[:10]:
            rows.append(
                Template(template_wujia).render(
                    date=record.get("date") or "--",
                    server=record.get("server") or "--",
                    price=_format_price(record.get("value")),
                )
            )
        tables[zone] = "\n".join(rows)
    return tables


async def get_wanbaolou_data(item_name: str) -> str:
    url = "https://trade-api.seasunwbl.com/api/buyer/goods/list"
    data = (
        await Request(
            url,
            params={
                "filter[role_appearance]": item_name,
                "filter[state]": 2,
                "goods_type": 3,
                "sort[price]": 1,
            },
        ).get()
    ).json()
    if data.get("code") == -11:
        return "万宝楼正在维护中……暂时没有数据"

    records = data.get("data", {}).get("list") or []
    rows = []
    for record in records[:6]:
        rows.append(
            Template(template_wujia).render(
                date=Time(Time().raw_time + record.get("remaining_time", 0)).format("%Y-%m-%d"),
                server=record.get("server_name") or "--",
                price=_format_price(float(record.get("single_unit_price") or 0) / 100),
            )
        )
    return "\n".join(rows)


def get_item_history(item_data: dict) -> tuple[list[float], list[str]]:
    all_records = []
    for group in item_data.get("list") or []:
        if isinstance(group, list):
            all_records.extend(record for record in group if isinstance(record, dict))
    records = [
        record for record in all_records
        if record.get("source") != 4 and record.get("date") and record.get("value") is not None
    ]
    if not records:
        records = [
            record for record in all_records
            if record.get("date") and record.get("value") is not None
        ]

    prices_by_date: dict[str, list[float]] = defaultdict(list)
    for record in records:
        prices_by_date[str(record["date"])].append(float(record["value"]))

    dates = sorted(prices_by_date)
    prices = [
        round(sum(prices_by_date[date]) / len(prices_by_date[date]), 2)
        for date in dates
    ]
    return prices, dates


def select_min_max(data: list[float], margin: float = 0.1, round_to: int = 10) -> tuple[int, int]:
    if not data:
        return 0, 100
    data_min = min(data)
    data_max = max(data)
    data_range = data_max - data_min
    if data_range == 0:
        data_range = max(data_max * margin, round_to)
    extend = data_range * margin
    optimal_min = max(0, data_min - extend)
    optimal_max = data_max + extend

    def round_down(value: float) -> float:
        return (value // round_to) * round_to

    def round_up(value: float) -> float:
        return ((value + round_to - 1) // round_to) * round_to

    return int(round_down(optimal_min)), int(round_up(optimal_max))


async def get_single_item_price(item_name: str, exact: bool = False) -> str | dict | list | None:
    query_name = item_name
    if not exact:
        local_data: ItemKeywordMap | None | Any = db.where_one(
            ItemKeywordMap(),
            "map_name = ?",
            item_name,
            default=None,
        )
        if local_data is not None:
            query_name = local_data.raw_name

    data = (
        await Request(
            f"{Config.jx3.api.url.rstrip('/')}/data/trade/records",
            params={"name": query_name, "token": Config.jx3.api.token},
        ).get()
    ).json()
    item_data = data.get("data")
    if data.get("code") != 200 or not isinstance(item_data, dict) or not item_data:
        return ["唔……未找到该物品！\n请确认是否应该使用“交易行”命令？"]

    final_item_name = str(item_data.get("name") or "未知")
    trade_data = get_item_price(item_data)
    wbl_data = await get_wanbaolou_data(final_item_name)
    prices, dates = get_item_history(item_data)
    y_min, y_max = select_min_max(prices)
    html = Template(read(build_path(TEMPLATES, ["jx3", "item_price.html"]))).render(
        font=build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
        item_image=str(item_data.get("view") or "https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/Unknown.png"),
        default_item_image="https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/Unknown.png",
        item_name=final_item_name,
        item_alias=str(item_data.get("alias") or "--"),
        custom_msg=str(item_data.get("desc") or "--"),
        publish_time=str(item_data.get("date") or "未知"),
        publish_price=_format_price(item_data.get("value")),
        trade_data=trade_data,
        wanbaolou=wbl_data,
        dates=json.dumps(dates, ensure_ascii=False),
        max=y_max,
        min=y_min,
        values=json.dumps(prices, ensure_ascii=False),
    )
    final_path = await generate(html, "body", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()
