from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path
from jinja2 import Template

from src.const.jx3.constant import server_aliases_data as servers
from src.const.path import ASSETS, build_path
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.time import Time
from src.templates import HTMLSourceCode

from ._template import table_dilu_head, template_dilu, good, bad

import json
import re
import time

brick = build_path(ASSETS, ["jx3", "trade", "brick.png"])
gold = build_path(ASSETS, ["jx3", "trade", "gold.png"])

class DiluData:
    def __init__(self, raw_data: Dict[str, Any]):
        self.raw_data = raw_data
        self.all_servers = list(servers)
        self.servers_data = {server: [] for server in self.all_servers}

    def convert_timestamp(self, ts: int) -> datetime:
        
        return datetime.fromtimestamp(ts)

    def format_time(self, dt: datetime) -> str:
        
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def is_within_current_week(self, dt: datetime) -> bool:
        
        now = datetime.now()
        if now.hour < 7:
            now -= timedelta(days=1)
        
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=7, minute=0, second=0, microsecond=0)

        return week_start <= dt <= now

    def as_jx3api(self) -> List[Dict[str, Any]]:
        
        for item in self.raw_data["rows"]:
            server = item['Srv']
            if server not in self.servers_data:
                continue
            
            row = {
                "server": server,
                "name": item["horsename"],
                "map_name": item["mapname"],
                "refresh_time": self.format_time(self.convert_timestamp(item["refreshtime"])),
                "capture_role_name": item["capturerolename"] or "尚未捕捉",
                "capture_camp_name": item["capturecampname"] or "未知",
                "capture_time": self.format_time(self.convert_timestamp(item["capturetime"])) if item["capturetime"] else "尚未捕捉",
                "auction_role_name": item["auctionrolename"] or "尚未竞拍",
                "auction_camp_name": item["auctioncampname"] or "未知",
                "auction_time": self.format_time(self.convert_timestamp(item["auctiontime"])) if item["auctiontime"] else "尚未竞拍",
                "auction_amount": item["auctionamount"] or "尚未竞拍"
            }
            if self.is_within_current_week(self.convert_timestamp(item["refreshtime"])):
                self.servers_data[server].append(row)

        final_data = []
        for server in self.all_servers:
            final_data.append({
                "server": server,
                "data": self.servers_data[server]
            })

        return final_data

async def get_dilu_raw_data():
    filter = {
        "Zone": "",
        "Srv": ""
    }
    params = {
        "sort": "id",
        "order": "desc",
        "limit": "21",
        "offset": "0",
        "filter": json.dumps(filter, ensure_ascii=False),
        "op": '{"Zone":"LIKE","Srv":"LIKE"}',
        "_": int(time.time()) * 1000
    }
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Microsoft Edge\";v=\"114\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "Referer": "https://www.jx3mm.com/jx3fun/jevent/jcitem.html"
    }
    data = (await Request("https://www.jx3mm.com/jx3fun/jevent/delu", headers=headers, params=params).get()).json()
    return data

async def get_dilu_data():
    raw_data = await get_dilu_raw_data()
    data = DiluData(raw_data).as_jx3api()
    table = []
    for i in data:
        if i["data"] == []:
            table.append(
                re.sub(
                    r"\{\{ .+? \}\}", "暂无信息",
                    template_dilu.replace("{{ server }}", i["server"])
                )
            )
        else:
            data_ = i["data"][0]
            server = i["server"]
            flush = "尚未刷新" if data_["refresh_time"] is None else data_["refresh_time"]
            capture = "尚未捕捉" if data_["capture_time"] is None else data_["capture_time"]
            auction = "尚未竞拍" if data_["auction_time"] is None else data_["auction_time"]
            map = data_["map_name"]
            capturer = "尚未捕捉" if data_["capture_role_name"] is None else data_["capture_role_name"]
            capturer_camp = "未知" if data_["capture_camp_name"] is None else data_["capture_camp_name"]
            bidder = "尚未竞拍" if data_["auction_role_name"] is None else data_["auction_role_name"]
            bidder_camp = "未知" if data_["auction_camp_name"] is None else data_["auction_camp_name"]
            ci = good if capturer_camp == "浩气盟" else bad
            bi = good if bidder_camp == "浩气盟" else bad
            price = "尚未竞拍" if data_["auction_amount"] is None else data_["auction_amount"].replace("万金","万0金").replace("万", f"<img src=\"{brick}\">").replace("金", f"<img src=\"{gold}\">")
            table.append(
                Template(template_dilu).render(
                    server = server,
                    flush = flush,
                    captured = capture,
                    sell = auction,
                    map = map,
                    capturer = capturer,
                    bi = bi,
                    ci = ci,
                    price = price,
                    auctioner = bidder,
                    bc = bidder_camp,
                    cc = capturer_camp
                )
            )
    html = str(
        HTMLSourceCode(
            application_name = f" · 的卢统计 · " + Time().format("%H:%M:%S"),
            table_head = table_dilu_head,
            table_body = "\n".join(table)
        )
    )
    final_path = await generate(html, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()