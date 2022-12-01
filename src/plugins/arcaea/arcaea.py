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
from file import read
from utils import get_api, convert_time, get_content

api = Config.auaurl
token = "Bearer " + Config.auatok
headers = {"Authorization": token}
difficulties = ["Past","Present","Future","Beyond"]
clear_statuses = ["Track Lost","Track Complete","Full Recall","Pure Memory","Easy Complete","Hard Complete"]

def judgeLevelByScore(score: int): # 来自Arcaea的评分标准 @OasisAkari
    '''
    使用分数进行等级判定。 @OasisAkari
    '''
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
    '''
    获取用户信息，使用用户码或者昵称。
    '''
    info = ""
    if nickname: # 如果使用昵称
        info = await get_api(api + f"user/info?user={nickname}&withsonginfo=true",headers=headers)
    elif usercode: # 如果使用UserCode
        info = await get_api(api + f"user/info?usercode={usercode}&withsonginfo=true",headers=headers)
    if info["status"] == -3:
        return "唔……用户不存在哦~"
    elif info["status"] == 0:
        account_info = info["content"]["account_info"]
        friend_code = account_info["code"] # 获取UserCode
        nickname = account_info["name"] # 获取昵称
        score = info["content"]["recent_score"][0]["score"] # 获取最近分数
        scoretype = judgeLevelByScore(score) # 根据上一行的分数得出等级
        clear_status = clear_statuses[info["content"]["recent_score"][0]["clear_type"]] # 获取过关状态
        difficulty = difficulties[info["content"]["recent_score"][0]["difficulty"]] # 获取难度
        memory = str(info["content"]["recent_score"][0]["health"]) + "%" # 获取记忆程度
        far = info["content"]["recent_score"][0]["near_count"] # 获取FAR的个数
        lost = info["content"]["recent_score"][0]["miss_count"] # 获取LOST的个数
        pure = info["content"]["recent_score"][0]["perfect_count"] # 获取PURE的个数
        song_ptt = info["content"]["recent_score"][0]["rating"] # 获取单曲PTT
        song_name = info["content"]["songinfo"][0]["name_en"] # 获取歌曲名称
        ptt = account_info["rating"] # 获取PTT
        song_icon = ms.image(await get_song(info["content"]["recent_score"][0]["song_id"])) # 获取歌曲Logo，使用`MessageSegment`转换为可发送的类型。
        register_time = convert_time(account_info["join_date"]) # 获取注册时间，使用转换函数，见src/tools/utils.py中的`convert_time`函数
        partner = ms.image(await get_char(account_info["character"])) # 获取搭档图片，使用`MessageSegment`转换为可发送的类型。
        play_time = convert_time(info["content"]["recent_score"][0]["time_played"]) # 获取玩家最近一次玩的时间，使用上述函数进行转换。
        return f"查询到玩家{nickname}（{friend_code}）：\n注册时间：{register_time}\nPTT：{ptt}\n" + song_icon + f"\n上次游玩：{song_name}（{difficulty}）\n{clear_status} {memory}\n分数：{score} {scoretype}\nPURE {pure} FAR {far} LOST {lost}\n游玩时间：{play_time}\n单曲PTT：{song_ptt}\n搭档：\n" + partner
    else:
        return "唔……查询失败，未知错误。"

async def judgeWhetherPlayer(usercode: int=None, nickname: str=None):
    '''
    判断玩家是否存在，使用用户码或者昵称。
    '''
    if nickname:
        info = await get_api(api + f"user/info?user={nickname}&withsonginfo=true",headers=headers)
    elif usercode:
        info = await get_api(api + f"user/info?usercode={usercode}&withsonginfo=true",headers=headers)
    data = info
    if data["status"] == 0:
        name = data["content"]["account_info"]["name"]
        code = data["content"]["account_info"]["code"]
        final = [name, code]
        return final # 相当于True（转换为`bool`之后）
    else:
        return False

def getUserCode(groupid:int, user: int):
    '''
    获取所在群聊某用户的绑定信息，需要的数据是群号和用户账号。
    '''
    userid = str(user)
    group = str(groupid)
    data = json.loads(read(DATA + "/" + group + "/arcaea.json"))
    try:
        usercode = data[userid]
        return usercode
    except KeyError: # 如果数据中不包含该用户的键值，则返回False。
        return False

async def get_char(char: int):
    '''
    获取搭档的照片，根据`account_info`的`character`获取，若本地有缓存，则优先使用本地的内容。
    
    具体实现可参考`get_song`的代码。
    '''
    if os.path.exists(ASSETS + f"/arcaea/char/{char}.png"):
        return Path(ASSETS + f"/arcaea/char/{char}.png").as_uri()
    else:
        url = f"{api}assets/char?partner={char}"
        cache = open(ASSETS + f"/arcaea/char/{char}.png", mode = "wb")
        try:
            cache.write(await get_content(url, headers = headers))
        except:
            raise HTTPError(f"Can't connect to {url}.")
        cache.close()
        return Path(ASSETS + f"/arcaea/char/{char}.png").as_uri()

async def get_song(song: str):
    '''
    获取歌曲的图片，根据发送给机器人的命令中的歌曲名，获取数据。

    若本地有缓存，则优先使用本地的内容。
    '''
    if os.path.exists(ASSETS + f"/arcaea/song/{song}.png"): # 判断是否存在本地文件
        return Path(ASSETS + f"/arcaea/song/{song}.png").as_uri() # 如果有，直接返回url。
    else:
        url = f"{api}assets/arcaea/song?file={song}" # 如果没有，开始从API下载。
        cache = open(ASSETS + f"/arcaea/song/{song}.png", mode = "wb") # 以二进制形式开始写入
        try:
            cache.write(await get_content(url, headers = headers)) # 写入
        except:
            raise HTTPError(f"Can't connect to {url}.") # 如果请求失败，则报错。
        cache.close() # 关闭文件对象
        return Path(ASSETS + f"/arcaea/song/{song}.png").as_uri() # 最后返回本地的路径，在assets/arcaea/song中。

async def getUserBestBySongName(usercode: int, songname: str, difficulty: str) -> str:
    '''
    获取用户最佳成绩，使用了用户码、歌曲名和难度。
    '''
    if difficulty in ["ftr","FTR","FUTURE","future","2","Future","Ftr"]: # 各种离谱的缩写，这里尽可能多地识别了。
        difficulty = "ftr"
    elif difficulty in ["pst","PST","past","Past","0","PAST","Pst"]:
        difficulty = "pst"
    elif difficulty in ["prs","present","1","Present","PRS","Prs"]:
        difficulty = "prs"
    elif difficulty in ["byd","byn","beyond","bey","3","Beyond","BEYOND","Byn","Byd"]:
        difficulty = "byn"
    else:
        return f"未找到您要的难度，可以使用0/1/2/3分别代替Past、Present、Future、Beyond哦~" # 实在离谱的话，来pr吧。
    url = api + f"user/best?usercode={usercode}&songname={songname}&difficulty={difficulty}&withrecent=true&withsonginfo=true"
    info = await get_api(url, headers=headers)
    if info["status"] == -15:
        return "尚未游玩这首歌曲。" # 没玩过，告知用户并催促赶紧去玩。
    song_name = info["content"]["songinfo"][0]["name_en"]
    if quote(song_name) == quote(songname): # 不能确保用户不会偷偷用%20这种（是的，百分号形式）。
        record = info["content"]["record"]
        player = info["content"]["account_info"]["name"] # 昵称
        code = info["content"]["account_info"]["code"] # 用户码
        char = ms.image(await get_char(info["content"]["account_info"]["character"])) # 获取搭档图片并转换为`MessageSegment`对象。
        score = record["score"] # 分数
        level = judgeLevelByScore(score) # 等级，通过分数划定。
        memory = str(record["health"]) + "%" # 回忆程度
        ptt = record["rating"] # 单曲PTT
        song = ms.image(await get_song(record["song_id"])) # 获取歌曲图片并转换为`MessageSegment`对象。
        difficulty = difficulties[record["difficulty"]] # 获取难度（标准写法）
        clear_status = clear_statuses[record["clear_type"]] # 获取过关状态。
        best_clear = clear_statuses[record["best_clear_type"]] # 获取最佳过关状态。
        time_played = convert_time(record["time_played"]) # 获取游玩时间，使用上述时间转换。
        far = record["near_count"] # FAR
        lost = record["miss_count"] # LOST
        pure = record["perfect_count"] # PURE
        return f"{player}/{code}：{song_name}（{difficulty}）\n" + song + f"\n" + char + f"分数：{score} {level}\n{clear_status} {memory}（最佳：{best_clear}）\n单曲PTT：{ptt}\nPURE {pure} FAR {far} LOST {lost}\n游玩时间：{time_played}"
    else:
        return "歌曲名不对哦，请检查后重试~"
    
