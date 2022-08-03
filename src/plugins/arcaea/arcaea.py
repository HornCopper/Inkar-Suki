import json
import sys
import nonebot
import os
from urllib.parse import quote
from pathlib import Path
from urllib.error import HTTPError
from nonebot.adapters.onebot.v11 import MessageSegment as ms
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
DATA = TOOLS[:-5] + "data"
ASSETS = TOOLS[:-5] + "assets"
from config import Config
from file import read, write
from utils import get_url, convert_time, get_content
from gender import uuid

api = Config.auaurl
token = Config.auatok
headers = {"User-Agent":token}
difficulties = ["Past","Present","Future","Beyond"]
clear_statuses = ["Track Lost","Track Complete","Full Recall","Pure Memory"]

def judgeLevelByScore(score: int):
    if score >= 9900000:
        scoretype = 'EX+'
    elif score >= 9800000:
        scoretype = 'EX'
    elif score >= 9500000:
        scoretype = 'AA'
    elif score >= 9200000:
        scoretype = 'A'
    elif score >= 8900000:
        scoretype = 'B'
    elif score >= 8600000:
        scoretype = 'C'
    else:
        scoretype = 'D'
    return scoretype

async def getUserInfo(nickname: str = None, usercode: int = None) -> str:
    info = ""
    if nickname:
        info = await get_url(api + f"user/info?user={nickname}&withsonginfo=true",headers=headers)
    elif usercode:
        info = await get_url(api + f"user/info?usercode={usercode}&withsonginfo=true",headers=headers)
    info = json.loads(info)
    if info["status"] == -3:
        return "唔……用户不存在哦~"
    elif info["status"] == 0:
        account_info = info["content"]["account_info"]
        friend_code = account_info["code"]
        nickname = account_info["name"]
        score = info["content"]["recent_score"][0]["score"]
        scoretype = judgeLevelByScore(score)
        clear_status = clear_statuses[info["content"]["recent_score"][0]["clear_type"]]
        difficulty = difficulties[info["content"]["recent_score"][0]["difficulty"]]
        memory = str(info["content"]["recent_score"][0]["health"]) + "%"
        far = info["content"]["recent_score"][0]["near_count"]
        lost = info["content"]["recent_score"][0]["miss_count"]
        pure = info["content"]["recent_score"][0]["perfect_count"]
        song_ptt = info["content"]["recent_score"][0]["rating"]
        song_name = info["content"]["songinfo"][0]["name_en"]
        ptt = info["content"]["account_info"]["rating"]
        song_icon = ms.image(await get_song(info["content"]["recent_score"][0]["song_id"]))
        register_time = convert_time(info["content"]["account_info"]["join_date"])
        partner = ms.image(await get_char(info["content"]["account_info"]["character"]))
        play_time = convert_time(info["content"]["recent_score"][0]["time_played"])
        return f"查询到玩家{nickname}（{friend_code}）：\n注册时间：{register_time}\nPTT：{ptt}\n" + song_icon + f"\n上次游玩：{song_name}（{difficulty}）\n{clear_status} {memory}\n分数：{score} {scoretype}\nPURE {pure} FAR {far} LOST {lost}\n游玩时间：{play_time}\n单曲PTT：{song_ptt}\n搭档：\n" + partner
    else:
        return "唔……查询失败，未知错误。"

async def judgeWhetherPlayer(usercode: int=None, nickname: str=None):
    if nickname:
        info = await get_url(api + f"user/info?user={nickname}&withsonginfo=true",headers=headers)
    elif usercode:
        info = await get_url(api + f"user/info?usercode={usercode}&withsonginfo=true",headers=headers)
    data = json.loads(info)
    if data["status"] == 0:
        name = data["content"]["account_info"]["name"]
        code = data["content"]["account_info"]["code"]
        final = [name, code]
        return final
    else:
        return False

def getUserCode(groupid:int, user: int):
    userid = str(user)
    group = str(groupid)
    data = json.loads(read(DATA + "/" + group + "/arcaea.json"))
    try:
        usercode = data[userid]
        return usercode
    except KeyError:
        return False

async def get_char(char: int):
    if os.path.exists(ASSETS + f"/char/{char}.png"):
        return Path(ASSETS + f"/char/{char}.png").as_uri()
    else:
        url = f"{api}assets/char?partner={char}"
        cache = open(ASSETS + f"/char/{char}.png", mode = "wb")
        try:
            cache.write(await get_content(url, headers = headers))
        except:
            raise HTTPError(f"Can't connect to {url}.")
        cache.close()
        return Path(ASSETS + f"/char/{char}.png").as_uri()

async def get_song(song: str):
    if os.path.exists(ASSETS + f"/song/{song}.png"):
        return Path(ASSETS + f"/song/{song}.png").as_uri()
    else:
        url = f"{api}assets/song?file={song}"
        cache = open(ASSETS + f"/song/{song}.png", mode = "wb")
        try:
            cache.write(await get_content(url, headers = headers))
        except:
            raise HTTPError(f"Can't connect to {url}.")
        cache.close()
        return Path(ASSETS + f"/song/{song}.png").as_uri()

async def getUserBestBySongName(usercode: int, songname: str, difficulty: str) -> str:
    if difficulty in ["ftr","FTR","FUTURE","future","2","Future","Ftr"]:
        difficulty = "ftr"
    elif difficulty in ["pst","PST","past","Past","0","PAST","Pst"]:
        difficulty = "pst"
    elif difficulty in ["prs","present","1","Present","PRS","Prs"]:
        difficulty = "prs"
    elif difficulty in ["byd","byn","beyond","bey","3","Beyond","BEYOND","Byn","Byd"]:
        difficulty = "byn"
    else:
        return f"未找到您要的难度，可以使用0/1/2/3分别代替Past、Present、Future、Beyond哦~"
    url = api + f"user/best?usercode={usercode}&songname={songname}&difficulty={difficulty}&withrecent=true&withsonginfo=true"
    info = json.loads(await get_url(url, headers=headers))
    song_name = info["content"]["songinfo"][0]["name_en"]
    if quote(song_name) == quote(songname):
        record = info["content"]["record"]
        player = info["content"]["account_info"]["name"]
        code = info["content"]["account_info"]["code"]
        char = ms.image(await get_char(info["content"]["account_info"]["character"]))
        score = record["score"]
        level = judgeLevelByScore(score)
        memory = str(record["health"]) + "%"
        ptt = record["rating"]
        song = ms.image(await get_song(record["song_id"]))
        difficulty = difficulties[record["difficulty"]]
        clear_status = clear_statuses[record["clear_type"]]
        best_clear = clear_statuses[record["best_clear_type"]]
        time_played = convert_time(record["time_played"])
        far = record["near_count"]
        lost = record["miss_count"]
        pure = record["perfect_count"]
        return f"{player}/{code}：{song_name}（{difficulty}）\n" + song + f"\n" + char + f"分数：{score} {level}\n{clear_status} {memory}（最佳：{best_clear}）\n单曲PTT：{ptt}\nPURE {pure} FAR {far} LOST {lost}\n游玩时间：{time_played}"
    else:
        return "歌曲名不对哦，请检查后重试~"
    