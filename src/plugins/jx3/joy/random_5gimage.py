from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from html import escape
from random import choice
from typing import Any

from jinja2 import Template

from src.config import Config
from src.const.path import ASSETS, build_path
from src.utils.analyze import sort_dict_list
from src.utils.database import logs_db
from src.utils.database.classes import RandomImageRecord
from src.utils.file import read
from src.utils.generate import generate
from src.utils.network import Request, cache_image
from src.utils.time import Time
from src.templates import HTMLSourceCode, get_saohua
from src.plugins.jx3.trade._parse import calculate_price, coin_to_image

from ._template import (
    table_random_5gimage_rank_head,
    table_random_5gimage_record_head,
    template_random_5gimage,
    template_random_5gimage_rank,
    template_random_5gimage_record,
)

import json

IMAGE_DATA_PATH = build_path(ASSETS, ["source", "jx3", "5g_images.json"])

IMAGE_INDEX_MAP = {
    "1": "壹",
    "2": "贰",
    "3": "叁",
    "4": "肆",
    "5": "伍",
    "6": "陆",
    "7": "柒",
    "8": "捌",
    "2N": "贰·新编",
}

IMAGE_NAME_PREFIX = "武技殊影图·"


@dataclass
class FiveGImageItem:
    name: str
    item_id: str
    icon_id: int | None

    @property
    def trade_item_id(self) -> str:
        if not self.item_id:
            raise ValueError(f"Item `{self.name}` has no item_id.")
        return "5_" + self.item_id

    @property
    def icon(self) -> str:
        if self.icon_id is None:
            raise ValueError(f"Item `{self.name}` has no icon_id.")
        return f"https://icon.jx3box.com/icon/{self.icon_id}.png"


@dataclass
class RandomFiveGImageResult:
    server: str
    box: FiveGImageItem
    opened: FiveGImageItem
    box_price: int | None
    opened_price: int | None

    @property
    def profit(self) -> int | None:
        if self.box_price is None or self.opened_price is None:
            return None
        return self.opened_price - self.box_price


def normalize_image_index(raw: str) -> str | None:
    raw = raw.strip().upper()
    return IMAGE_INDEX_MAP.get(raw)


def load_image_box(index_name: str) -> tuple[FiveGImageItem, list[FiveGImageItem]] | None:
    data = json.loads(read(IMAGE_DATA_PATH))
    box_name = f"武技殊影图·{index_name}"
    for box in data.get("boxes", []):
        if box.get("name") != box_name:
            continue
        box_item = FiveGImageItem(
            name=str(box.get("name", "")),
            item_id=str(box.get("item_id", "")),
            icon_id=box.get("icon_id"),
        )
        items = [
            FiveGImageItem(
                name=str(item.get("name", "")),
                item_id=str(item.get("item_id", "")),
                icon_id=item.get("icon_id"),
            )
            for item in box.get("items", [])
        ]
        return box_item, items
    return None


@cache
def load_image_items_by_id() -> dict[str, FiveGImageItem]:
    data = json.loads(read(IMAGE_DATA_PATH))
    items: dict[str, FiveGImageItem] = {}
    for box in data.get("boxes", []):
        box_item = FiveGImageItem(
            name=str(box.get("name", "")),
            item_id=str(box.get("item_id", "")),
            icon_id=box.get("icon_id"),
        )
        if box_item.item_id:
            items[box_item.item_id] = box_item
        for item in box.get("items", []):
            image_item = FiveGImageItem(
                name=str(item.get("name", "")),
                item_id=str(item.get("item_id", "")),
                icon_id=item.get("icon_id"),
            )
            if image_item.item_id:
                items[image_item.item_id] = image_item
    return items


def trim_image_name(name: str) -> str:
    return name.removeprefix(IMAGE_NAME_PREFIX)


def format_image_item(name: str, item_id: str) -> str:
    display_name = escape(trim_image_name(name))
    item = load_image_items_by_id().get(str(item_id or ""))
    if item is None or item.icon_id is None:
        return f'<span class="record-item">{display_name}</span>'
    return (
        '<span class="record-item">'
        f'<img src="{escape(item.icon)}" alt="">'
        f"{display_name}"
        "</span>"
    )


async def get_latest_trade_price(server: str, item_id: str) -> int | None:
    url = "https://next2.jx3box.com/api/auction/"
    params = {"server": server, "item_id": item_id, "aggregate_type": "hourly"}
    data: list[dict[str, Any]] = (await Request(url, params=params).post()).json()
    if not data:
        params["aggregate_type"] = "daily"
        data = (await Request(url, params=params).post()).json()
    if not data:
        return None
    return int(sort_dict_list(data, "timestamp")[-1]["price"])


def format_price(price: int | None) -> str:
    if price is None:
        return '<span class="no-price">暂无数据</span>'
    return coin_to_image(calculate_price(price))


def format_signed_price(price: int) -> str:
    prefix = "+" if price > 0 else ""
    return prefix + coin_to_image(calculate_price(price))


def format_signed_text(price: int) -> str:
    prefix = "+" if price > 0 else ""
    return prefix + calculate_price(price)


def profit_class(price: int, base_class: str = "price-cell") -> str:
    if price > 0:
        return f"{base_class} profit-plus"
    if price < 0:
        return f"{base_class} profit-minus"
    return base_class


async def render_random_5gimage(result: RandomFiveGImageResult):
    box_icon = await cache_image(result.box.icon) if result.box.icon else ""
    opened_icon = await cache_image(result.opened.icon) if result.opened.icon else ""
    profit = result.profit
    profit_text = "无法计算" if profit is None else format_signed_price(profit)
    profit_class = "neutral" if profit is None or profit == 0 else ("plus" if profit > 0 else "minus")
    html = Template(template_random_5gimage).render(
        font=build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"]),
        box_icon=box_icon,
        box_name=trim_image_name(result.box.name),
        box_price=format_price(result.box_price),
        opened_icon=opened_icon,
        opened_name=trim_image_name(result.opened.name),
        opened_price=format_price(result.opened_price),
        profit=profit_text,
        profit_class=profit_class,
        server=result.server,
        appinfo=f"随机武技图 · {result.server}",
        bot_name=Config.bot_basic.bot_name_argument,
        saohua=get_saohua(),
    )
    return await generate(html, ".card", segment=True, wait_for_network=True)


async def generate_random_5gimage(server: str, index_name: str, user_id: int, group_id: int):
    loaded = load_image_box(index_name)
    if loaded is None:
        return None
    box, items = loaded
    if not items:
        return None
    opened = choice(items)
    box_price = await get_latest_trade_price(server, box.trade_item_id)
    opened_price = await get_latest_trade_price(server, opened.trade_item_id)
    result = RandomFiveGImageResult(
        server=server,
        box=box,
        opened=opened,
        box_price=box_price,
        opened_price=opened_price,
    )
    if result.profit is not None:
        logs_db.save(
            RandomImageRecord(
                user_id=user_id,
                group_id=group_id,
                server=server,
                box_name=box.name,
                box_item_id=box.item_id,
                box_price=box_price or 0,
                result_name=opened.name,
                result_item_id=opened.item_id,
                result_price=opened_price or 0,
                profit=result.profit,
                timestamp=Time().raw_time,
            )
        )
    return await render_random_5gimage(result), result.profit is not None


async def get_random_5gimage_record_image(user_id: int, group_id: int):
    records: list[RandomImageRecord] | Any = logs_db.where_all(
        RandomImageRecord(),
        "user_id = ? AND group_id = ?",
        user_id,
        group_id,
        default=[],
    )
    if not records:
        return "还没有开图记录。"
    records = sorted(records, key=lambda record: record.timestamp, reverse=True)
    total_profit = sum(record.profit for record in records)
    table_body = []
    for record in records[:30]:
        table_body.append(
            Template(template_random_5gimage_record).render(
                time=Time(record.timestamp).format("%Y-%m-%d %H:%M:%S"),
                server=record.server,
                box_name=format_image_item(record.box_name, record.box_item_id),
                result_name=format_image_item(record.result_name, record.result_item_id),
                box_price=format_price(record.box_price),
                result_price=format_price(record.result_price),
                profit=format_signed_price(record.profit),
                profit_class=profit_class(record.profit),
            )
        )
    css = """
.item-table td img {
  vertical-align: -3px;
  margin: 0 2px;
}
.record-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}
.record-item img {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  object-fit: cover;
  margin: 0;
}
.profit-plus {
  color: #1f8f55;
}
.profit-minus {
  color: #c24141;
}
"""
    html = str(
        HTMLSourceCode(
            application_name=f"开图战绩 · {len(records)}次 · 累计盈亏 {format_signed_text(total_profit)}",
            table_head=table_random_5gimage_record_head,
            table_body="\n".join(table_body),
            additional_css=css,
        )
    )
    return await generate(html, ".container", segment=True, wait_for_network=True)


async def get_random_5gimage_rank_image(bot: Any, group_id: int):
    records: list[RandomImageRecord] | Any = logs_db.where_all(
        RandomImageRecord(),
        "group_id = ?",
        group_id,
        default=[],
    )
    if not records:
        return "还没有开图记录。"

    grouped: dict[int, dict[str, int]] = {}
    for record in records:
        user_data = grouped.setdefault(record.user_id, {"count": 0, "profit": 0})
        user_data["count"] += 1
        user_data["profit"] += record.profit

    members = await bot.get_group_member_list(group_id=group_id)
    member_map = {int(member["user_id"]): member for member in members}
    ranked = sorted(
        grouped.items(),
        key=lambda item: (item[1]["profit"], item[1]["count"]),
        reverse=True,
    )

    table_body = []
    for rank, (user_id, data) in enumerate(ranked[:30], start=1):
        member = member_map.get(user_id, {})
        nickname = (member.get("card") or member.get("nickname") or str(user_id))[:15]
        total_profit = data["profit"]
        avg_profit = int(total_profit / data["count"])
        table_body.append(
            Template(template_random_5gimage_rank).render(
                rank=rank,
                avatar=f"https://q.qlogo.cn/headimg_dl?dst_uin={user_id}&spec=100&img_type=jpg",
                nickname=nickname,
                count=data["count"],
                total_profit=format_signed_price(total_profit),
                avg_profit=format_signed_price(avg_profit),
                total_class=profit_class(total_profit),
                avg_class=profit_class(avg_profit),
            )
        )

    css = """
.item-table td img {
  vertical-align: -3px;
  margin: 0 2px;
}
.item-table td img.rank-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  object-fit: cover;
}
.profit-plus {
  color: #1f8f55;
}
.profit-minus {
  color: #c24141;
}
"""
    html = str(
        HTMLSourceCode(
            application_name=f"开图排行 · {len(ranked)}人",
            table_head=table_random_5gimage_rank_head,
            table_body="\n".join(table_body),
            additional_css=css,
        )
    )
    return await generate(html, ".container", segment=True, wait_for_network=True)
