from datetime import datetime, timedelta

from src.const.path import ASSETS
from src.utils.analyze import sort_dict_list
from src.utils.network import Request
from src.utils.generate import generate
from src.templates import SimpleHTML

from ._template import (
    koromo_api_sp as sp,
    koromo_api_pr as pr,
    koromo_api_ps as ps,
    koromo_api_pes as pes
)

import json

def get_previous_month(date_str: str = "") -> str:
    date_obj = datetime.today()
    if date_obj.month == 1:
        previous_month = datetime(date_obj.year - 1, 12, 1)
    else:
        previous_month = datetime(date_obj.year, date_obj.month - 1, 1)
    return previous_month.strftime("%Y-%m")

def get_month_timestamps(month_str: str) -> tuple[int, int]:
    start_date = datetime.strptime(month_str, "%Y-%m")
    start_timestamp = int(start_date.timestamp())
    if start_date.month == 12:
        end_date = datetime(start_date.year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_date = datetime(start_date.year, start_date.month + 1, 1) - timedelta(seconds=1)
    end_timestamp = int(end_date.timestamp())
    return start_timestamp, end_timestamp

class MSMRG: # Majsoul Monthly Report Generator
    search_player_url = sp
    player_record_url = pr.replace("limit=8&", "")
    player_stats_url = ps
    player_extended_stats_url = pes

    mode = "16.12.9.15.11.8"

    def __init__(self, role_id: int = 0, role_name: str = "", month: str = ""):
        self.role_id = role_id
        self.role_name = role_name
        self.month = month

    @classmethod
    async def with_role_name(cls, name: str, month: str = get_previous_month()) -> "MSMRG | str":
        possible_roles: list[dict] = (
            await Request(
                cls.search_player_url.format(player=name)
            ).get()
        ).json()
        if len(possible_roles) == 0:
            return "未找到该玩家，请检查后重试！"
        return cls(possible_roles[0]["id"], possible_roles[0]["nickname"], month)
    
    async def get_information(self):
        time_start, time_end = get_month_timestamps(self.month)
        player_records: list[dict] = (
            await Request(
                self.player_record_url.format(
                    player_id=str(self.role_id),
                    end_timestamp=str(time_end*1000),
                    start_timestamp=str(time_start*1000),
                    mode=self.mode
                )
            ).get()
        ).json()
        player_stats: dict[str, float] = (
            await Request(
                self.player_extended_stats_url.format(
                    player_id=str(self.role_id),
                    end_timestamp=str(time_end*1000),
                    start_timestamp=str(time_start*1000),
                    mode=self.mode
                )
            ).get()
        ).json()
        self.records = player_records
        self.stats = player_stats
        
    @property
    def count(self):
        return str(len(self.records))
    
    def rank_count(self, rank: int) -> int:
        count = 0
        for each_game in self.records:
            if sort_dict_list(each_game["players"], "score")[::-1][rank - 1]["accountId"] == self.role_id:
                count += 1
        return count

    @property
    def pt_change(self) -> str:
        count = 0
        for each_game in self.records:
            for player in each_game["players"]:
                if player["accountId"] == self.role_id:
                    count += player["gradingScore"]
        return "+" + str(count) if count >= 0 else str(count)
    
    @property
    def pt_changes(self) -> str:
        changes = []
        for each_game in self.records:
            for player in each_game["players"]:
                if player["accountId"] == self.role_id:
                    changes.append(
                        player["gradingScore"]
                    )
        return json.dumps(changes, ensure_ascii=False)
    
    @property
    def avg_rank(self) -> str:
        total = 0
        for rank in range(4):
            total += (rank + 1)*self.rank_count(rank + 1)
        return str(round(total / int(self.count), 2))
    
    @staticmethod
    def percent(x: float):
        return str(round(x*100, 2)) + "%"

    @property # 立直 副露 和牌 放铳 默听 打点 铳点
    def basic_attr(self) -> list[dict[str, str]]:
        data = self.stats
        values = [
            {
                attr:
                self.percent(data.get(attr, 0))
            }
            for attr
            in ["立直率", "副露率", "和牌率", "放铳率", "默听率"]
        ]
        values += [
                {
                    attr:
                    str(data.get(attr, 0))
                }
                for attr
                in ["平均打点", "平均铳点"]
            ]
        return values
    
    async def get_pt(self) -> int:
        time_start, time_end = get_month_timestamps(self.month)
        player_stats: dict = (
            await Request(
                self.player_stats_url.format(
                    player_id=str(self.role_id),
                    end_timestamp=str(time_end*1000),
                    start_timestamp=str(time_start*1000),
                    mode=self.mode
                )
            ).get()
        ).json()
        return player_stats["level"]["score"] + player_stats["level"]["delta"]

    async def generate_image(self):
        await self.get_information()
        input_data = {}
        input_data["nickname"] = self.role_name
        input_data["id"] = self.role_id
        input_data["count"] = self.count
        input_data["total_pt"] = self.pt_change
        basic_attr = self.basic_attr
        final_attr = {key: next(d[key] for d in basic_attr if key in d) for key in {k for d in basic_attr for k in d}}
        input_data["show_data"] = final_attr
        input_data["rank_data"] = zip(
            ["一位", "二位", "三位", "四位"],
            [
                str(self.rank_count(rank + 1))
                for rank
                in range(4)
            ],
            [
                self.percent(
                    self.rank_count(rank + 1) / int(self.count)
                )
                for rank
                in range(4)
            ]
        )
        input_data["pt_change"] = self.pt_changes
        input_data["init_pt"] = str(
            (await self.get_pt()) - int(self.pt_change)
        )
        input_data["month"] = self.month
        input_data["font"] = ASSETS + "/font/PingFangSC-Semibold.otf"
        input_data["avg_rank"] = self.avg_rank
        html = str(
            SimpleHTML(
                html_type="majsoul",
                html_template="majsoul_monthly_report.html",
                **input_data
            )
        )
        return await generate(html, ".container", first=True, segment=True)