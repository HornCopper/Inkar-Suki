from pathlib import Path
from jinja2 import Template

from src.utils.network import Request
from src.utils.time import Time
from src.templates import SimpleHTML
from src.const.path import ASSETS, CACHE
from src.utils.generate import generate

import math
import random

from ._template import (
    koromo_api_sp,
    koromo_api_ps,
    koromo_api_pr,
    gamemode,
    max_points,
    template_majsoul_record
)

def sort_list_of_dicts(list_of_dicts, key_name):
    sorted_list = sorted(list_of_dicts, key=lambda x: x[key_name])
    return sorted_list

def getRank(raw_data: dict | int) -> str:
    if isinstance(raw_data, dict):
        id = raw_data["level"]["id"]
    elif isinstance(raw_data, int):
        id = raw_data
    major = id % 10000
    minor = math.floor(major / 100)
    rank = "初士杰豪圣"[minor-1] if minor != 7 else "魂天"
    label = rank + str(major % 100)
    return label

async def find_player(keyword: str) -> str:
    final_url = koromo_api_sp.format(player=keyword)
    data = (await Request(final_url).get()).json()
    msg = "查找到下列玩家：\n"
    if len(data) == 0:
        return "未找到任何玩家！"
    for i in data:
        msg += f"[{getRank(i)}] " + i["nickname"] + "\n"
    return msg[:-1]

async def get_id_by_name(keyword: str, mode: str = "16.12.9.15.11.8") -> list | int:
    final_url = koromo_api_sp.format(player=keyword)
    data = (await Request(final_url).get()).json()
    if len(data) == 0:
        return ["未找到任何玩家，或者该ID不准确，请检查后重试！"]
    else:
        return data[0]["id"]

def get_mode_name(mode: int) -> str | None:
    for i in gamemode:
        if mode == gamemode[i]:
            return i

def get_player_sort(player: int, sorted_data: list) -> str | None:
    for i in sorted_data:
        if player == i["accountId"]:
            return "一二三四"[sorted_data.index(i)]

def process_number(string_num: str) -> str:
    int_num = int(string_num)
    if int_num > 0:
        return "<span style=\"color:green\">+" + string_num + "</span>"
    elif int_num < 0:
        return "<span style=\"color:red\">" + string_num + "</span>"
    else:
        return string_num

def process_nickname(string: str, match: str) -> str:
    if match == string:
        return "<span style=\"color:gold\"><b>" + string + "</b></span>"
    else:
        return string
    
async def player_pt(name: str = "", mode="16.12.9.15.11.8") -> str:
    if name is None:
        return "请输入玩家名！"
    pid = await get_id_by_name(name)
    if isinstance(pid, list):
        return pid[0]
    final_url = koromo_api_ps.format(player_id=pid, end_timestamp=str(Time().raw_time*1000), start_timestamp="1262304000000", mode=mode)
    data = (await Request(final_url).get()).json()
    rank = getRank(data["level"]["id"])
    level = max_points[rank] if rank[0] != "魂" else "20.0"
    score = str(data["level"]["score"] + data["level"]["delta"]) if rank[0] != "魂" else str(round((data["level"]["score"] + data["level"]["delta"]) / 100, 1))
    rank_max = getRank(data["max_level"]["id"])
    level_max = max_points[rank_max] if rank[0] != "魂" else "20.0"
    score_max = str(data["max_level"]["score"] + data["max_level"]["delta"]) if rank[0] != "魂" else str(round((data["level"]["score"] + data["level"]["delta"]) / 100, 1))
    return f"[{rank}] {name}（{pid}）\n当前PT：[{rank}] {score}/{level}\n最高PT：[{rank_max}] {score_max}/{level_max}"

async def get_records(name: str = "", mode: str = "16.12.9.15.11.8") -> str | list | None:
    if name is None:
        return "请输入玩家名！"
    pid = await get_id_by_name(name)
    if isinstance(pid, list):
        return pid[0]
    final_url = koromo_api_pr.format(player_id=pid, end_timestamp=str(Time().raw_time*1000), start_timestamp="1262304000000", mode=mode)
    data = (await Request(final_url).get()).json()
    if data == {}:
        return "PID输入错误，或该玩家没有任何记录！"
    else:
        tables = []
        for i in data:
            level = get_mode_name(i["modeId"])
            sorted_players = list(reversed(sort_list_of_dicts(i["players"], "score")))
            place = get_player_sort(pid, sorted_players)
            done_time = Time(i["endTime"]).format("%Y-%m-%d<br>%H:%M:%S") 
            name_1st = "[" + getRank(sorted_players[0]["level"]) + "] " + process_nickname(sorted_players[0]["nickname"], name)
            name_2nd = "[" + getRank(sorted_players[1]["level"]) + "] " + process_nickname(sorted_players[1]["nickname"], name)
            name_3rd = "[" + getRank(sorted_players[2]["level"]) + "] " + process_nickname(sorted_players[2]["nickname"], name)
            name_4th = "[" + getRank(sorted_players[3]["level"]) + "] " + process_nickname(sorted_players[3]["nickname"], name)
            score_1st = str(sorted_players[0]["score"])
            score_2nd = str(sorted_players[1]["score"])
            score_3rd = str(sorted_players[2]["score"])
            score_4th = str(sorted_players[3]["score"])
            grading_1st = process_number(str(sorted_players[0]["gradingScore"]))
            grading_2nd = process_number(str(sorted_players[1]["gradingScore"]))
            grading_3rd = process_number(str(sorted_players[2]["gradingScore"]))
            grading_4th = process_number(str(sorted_players[3]["gradingScore"]))
            template = Template(template_majsoul_record).render(
                level = level,
                num = place,
                time = done_time,
                _1st = name_1st,
                _2nd = name_2nd,
                _3rd = name_3rd,
                _4th = name_4th,
                sc1 = score_1st,
                sc2 = score_2nd,
                sc3 = score_3rd,
                sc4 = score_4th,
                gr1 = grading_1st,
                gr2 = grading_2nd,
                gr3 = grading_3rd,
                gr4 = grading_4th
            )
            tables.append(template)
        html = str(
            SimpleHTML(
                "majsoul",
                "majsoul_record",
                player_name = name,
                table_content = "\n".join(tables)
            )
        )
        final_path = await generate(html, ".background-container", False)
        if not isinstance(final_path, str):
            return
        return [Path(final_path).as_uri()]