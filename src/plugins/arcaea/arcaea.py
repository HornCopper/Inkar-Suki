import json
import sys
import nonebot
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
from config import Config
from utils import get_url, convert_time

api = Config.auaurl
token = Config.auatok
headers = {"User-Agent":token}
difficulties = ["Past","Present","Future"]

async def getUserInfo(nickname: str = None, usercode: int = None) -> str:
    if nickname:
        info = await get_url(api+f"user/info?user={nickname}&withsonginfo=true",headers=headers)
    elif usercode:
        info = await get_url(api+f"user/info?usercode={usercode}&withsonginfo=true",headers=headers)
    info = json.loads(info)
    if info["status"] == -3:
        return "唔……用户不存在哦，请尝试使用好友码搜索~"
    elif info["status"] == 0:
        account_info = info["content"]["account_info"]
        friend_code = account_info["code"]
        nickname = account_info["name"]
        lst_score = info["content"]["recent_score"][0]["score"]
        difficulty = difficulties[info["content"]["recent_score"][0]["difficulty"]]
        far = info["content"]["recent_score"][0]["near_count"]
        lost = info["content"]["recent_score"][0]["miss_count"]
        song_name = info["content"]["songinfo"][0]["name_en"]
        register_time = convert_time(info["content"]["account_info"]["join_date"])
        play_time = convert_time(info["content"]["recent_score"][0]["time_played"])
        return f"查询到玩家{nickname}（{friend_code}）：\n注册时间：{register_time}\n上次游玩：{song_name}（{difficulty}）\n分数：{lst_score}\nFAR {far} LOST {lost}\n游玩时间：{play_time}"
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