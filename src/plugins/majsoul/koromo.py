from pathlib import Path
from typing import Optional, Union

from src.tools.utils.request import get_api
from src.tools.utils.time import convert_time, get_current_time
from src.tools.utils.file import read, write
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.generate import get_uuid, generate

import math
import random

gamemode = {
    "金东": 8,
    "金": 9,
    "玉东": 11,
    "玉": 12,
    "王东": 15,
    "王座": 16,
    "三金东": 21,
    "三金": 22,
    "三玉东": 23,
    "三玉": 24,
    "三王东": 25,
    "三王座": 26,
}

koromo_api_sp = "https://5-data.amae-koromo.com/api/v2/pl4/search_player/{player}?limit=20&tag=all" 

koromo_api_pr = "https://5-data.amae-koromo.com/api/v2/pl4/player_records/{player_id}/{end_timestamp}/{start_timestamp}?limit=5&mode={mode}&descending=true"

koromo_api_ps = "https://5-data.amae-koromo.com/api/v2/pl4/player_stats/{player_id}/{start_timestamp}/{end_timestamp}?mode={mode}"

def sort_list_of_dicts(list_of_dicts, key_name):
    sorted_list = sorted(list_of_dicts, key=lambda x: x[key_name])
    return sorted_list

def getRank(raw_data):
    if type(raw_data) == type({}):
        id = raw_data["level"]["id"]
    elif type(raw_data) == type(1): # Accept both `int` and `dict`
        id = raw_data
    major = id % 10000
    minor = math.floor(major / 100)
    rank = "初士杰豪圣"[minor-1] if minor != 7 else "魂天"
    label = rank + str(major % 100)
    return label

async def find_player(keyword: str):
    final_url = koromo_api_sp.format(player=keyword)
    data = await get_api(final_url)
    msg = "查找到下列玩家：\n"
    if len(data) == 0:
        return "未找到任何玩家！"
    for i in data:
        msg += f"[{getRank(i)}] " + i["nickname"] + "\n"
    return msg[:-1]

async def get_id_by_name(keyword: str, mode: str = "16.12.9.15.11.8"):
    final_url = koromo_api_sp.format(player=keyword)
    data = await get_api(final_url)
    if len(data) == 0:
        return ["未找到任何玩家，或者该ID不准确，请检查后重试！"]
    else:
        return data[0]["id"]

def get_mode_name(mode: int):
    for i in gamemode:
        if mode == gamemode[i]:
            return i

def get_player_sort(player: int, sorted_data: dict):
    for i in sorted_data:
        if player == i["accountId"]:
            return "一二三四"[sorted_data.index(i)]  # type: ignore

template_majsoul_record = """
<tr>
    <td>$level</td>
    <td>$num</td>
    <td>$1st<br>（$sc1）<br>$gr1</td>
    <td>$2nd<br>（$sc2）<br>$gr2</td>
    <td>$3rd<br>（$sc3）<br>$gr3</td>
    <td>$4th<br>（$sc4）<br>$gr4</td>
    <td>$time</td>
</tr>"""

max_points = {
    "初1": 20,
    "初2": 80,
    "初3": 200,
    "士1": 600,
    "士2": 800,
    "士3": 1000,
    "杰1": 1200,
    "杰2": 1400,
    "杰3": 2000,
    "豪1": 2800,
    "豪2": 3200,
    "豪3": 3600,
    "圣1": 4000,
    "圣2": 6000,
    "圣3": 9000
}

def process_number(string_num: str):
    int_num = int(string_num)
    if int_num > 0:
        return "<span style=\"color:green\">+" + string_num + "</span>"
    elif int_num < 0:
        return "<span style=\"color:red\">" + string_num + "</span>"
    else:
        return string_num

def process_nickname(string: str, match: str):
    if match == string:
        return "<span style=\"color:gold\"><b>" + string + "</b></span>"
    else:
        return string
    
async def player_pt(name: str = "", mode="16.12.9.15.11.8"):
    if name is None:
        return "请输入玩家名！"
    pid = await get_id_by_name(name)
    if type(pid) == type([]):
        return pid[0]
    final_url = koromo_api_ps.format(player_id=pid, end_timestamp=str(get_current_time()*1000), start_timestamp="1262304000000", mode=mode)
    data = await get_api(final_url)
    rank = getRank(data["level"]["id"])
    level = max_points[rank] if rank[0] != "魂" else "20.0"
    score = str(data["level"]["score"] + data["level"]["delta"]) if rank[0] != "魂" else str(round((data["level"]["score"] + data["level"]["delta"]) / 100, 1))
    rank_max = getRank(data["max_level"]["id"])
    level_max = max_points[rank_max] if rank[0] != "魂" else "20.0"
    score_max = str(data["max_level"]["score"] + data["max_level"]["delta"]) if rank[0] != "魂" else str(round((data["level"]["score"] + data["level"]["delta"]) / 100, 1))
    return f"[{rank}] {name}（{pid}）\n当前PT：[{rank}] {score}/{level}\n最高PT：[{rank_max}] {score_max}/{level_max}"

async def get_records(name: str = "", mode: str = "16.12.9.15.11.8") -> Union[Optional[str], list]:
    if name is None:
        return "请输入玩家名！"
    pid = await get_id_by_name(name)
    if type(pid) == type([]):
        return pid[0]
    final_url = koromo_api_pr.format(player_id=pid, end_timestamp=str(get_current_time()*1000), start_timestamp="1262304000000", mode=mode)
    data = await get_api(final_url)
    if data == {}:
        return "PID输入错误，或该玩家没有任何记录！"
    else:
        tables = []
        for i in data:
            level = get_mode_name(i["modeId"])
            sorted_players = list(reversed(sort_list_of_dicts(i["players"], "score")))
            place = get_player_sort(pid, sorted_players)  # type: ignore
            done_time = convert_time(i["endTime"], "%Y-%m-%d<br>%H:%M:%S") 
            template = template_majsoul_record.replace("$level", level).replace("$num", place).replace("$time", done_time)  # type: ignore
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
            template = template.replace("$1st", name_1st).replace("$sc1", score_1st).replace("$gr1", grading_1st)
            template = template.replace("$2nd", name_2nd).replace("$sc2", score_2nd).replace("$gr2", grading_2nd)
            template = template.replace("$3rd", name_3rd).replace("$sc3", score_3rd).replace("$gr3", grading_3rd)
            template = template.replace("$4th", name_4th).replace("$sc4", score_4th).replace("$gr4", grading_4th)
            tables.append(template)
        rdbg = ASSETS + "/majsoul/" + str(random.randint(0, 44)) + ".jpg"
        html = read(VIEWS + "/majsoul/record/record.html")
        html = html.replace("$player_name", name).replace("$tablecontent", "\n".join(tables)).replace("$rdbg", rdbg)
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, ".background-container", False)
        if not isinstance(final_path, str):
            return
        return [Path(final_path).as_uri()]