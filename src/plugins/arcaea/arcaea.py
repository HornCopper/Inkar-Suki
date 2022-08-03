import json
import sys
import nonebot
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
DATA = TOOLS[:-5] + "data"
from config import Config
from file import read, write
from utils import get_url, convert_time

api = Config.auaurl
token = Config.auatok
headers = {"User-Agent":token}
difficulties = ["Past","Present","Future","Beyond"]
clear_statuses = ["Track Lost","Track Complete","Full Recall","Pure Memory"]

async def getUserInfo(nickname: str = None, usercode: int = None) -> str:
    info = ""
    if nickname:
        info = await get_url(api+f"user/info?user={nickname}&withsonginfo=true",headers=headers)
    elif usercode:
        info = await get_url(api+f"user/info?usercode={usercode}&withsonginfo=true",headers=headers)
    info = json.loads(info)
    if info["status"] == -3:
        return "唔……用户不存在哦~"
    elif info["status"] == 0:
        account_info = info["content"]["account_info"]
        friend_code = account_info["code"]
        nickname = account_info["name"]
        score = info["content"]["recent_score"][0]["score"]
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
        clear_status = clear_statuses[info["content"]["recent_score"][0]["clear_type"]]
        difficulty = difficulties[info["content"]["recent_score"][0]["difficulty"]]
        far = info["content"]["recent_score"][0]["near_count"]
        lost = info["content"]["recent_score"][0]["miss_count"]
        song_name = info["content"]["songinfo"][0]["name_en"]
        register_time = convert_time(info["content"]["account_info"]["join_date"])
        play_time = convert_time(info["content"]["recent_score"][0]["time_played"])
        return f"查询到玩家{nickname}（{friend_code}）：\n注册时间：{register_time}\n上次游玩：{song_name}（{difficulty}）\n{clear_status}\n分数：{score} {scoretype}\nFAR {far} LOST {lost}\n游玩时间：{play_time}"
    else:
        return "唔……查询失败，未知错误。"

async def judgeWhetherPlayer(usercode: int=None, nickname: str=None):
    if nickname:
        info = await get_url(api+f"user/info?user={nickname}&withsonginfo=true",headers=headers)
    elif usercode:
        info = await get_url(api+f"user/info?usercode={usercode}&withsonginfo=true",headers=headers)
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