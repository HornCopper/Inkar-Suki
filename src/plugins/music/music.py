import nonebot
import sys

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from utils import get_api
from config import Config

async def search(platform: bool, song: str):
    '''
    搜索型函数。

    返回搜索结果。

    第一个参数是平台，类型为`bool`，若为`True`则识别为`QQ音乐`，反之则为`网易云音乐`。
    '''
    copper_api_token = Config.coppertoken
    if platform:
        if copper_api_token:
            final_link = "https://copper.codethink.cn/music?platform=tencent&song=" + song + "&token=" + copper_api_token
        else:
            final_link = "https://www.jx3api.com/data/music/tencent?name=" + song
    else:
        if copper_api_token:
            final_link = "https://copper.codethink.cn/music?platform=netease&song=" + song + "&token=" + copper_api_token
        else:
            final_link = "https://www.jx3api.com/data/music/netease?name=" + song
    data = await get_api(final_link)
    if data["code"] == 404:
        return "未收录该歌曲，请检查后重试~"
    else:
        music = []
        id = []
        data = data["data"]
        for i in data:
            song = i["name"] + " - " + i["singer"]
            music.append(song)
            id.append(i["id"])
        return [music, id]

async def get(platform: bool, song: str, singer: str = None):
    '''
    请求型函数。

    返回第一搜索结果。

    第一个参数是平台，类型为`bool`，若为`True`则识别为`QQ音乐`，反之则为`网易云音乐`。
    '''
    copper_api_token = Config.coppertoken
    if platform:
        if copper_api_token:
            final_link = "https://copper.codethink.cn/music?platform=tencent&song=" + song + "&token=" + copper_api_token
        else:
            final_link = "https://www.jx3api.com/data/music/tencent?name=" + song
    else:
        if copper_api_token:
            final_link = "https://copper.codethink.cn/music?platform=netease&song=" + song + "&token=" + copper_api_token
        else:
            final_link = "https://www.jx3api.com/data/music/netease?name=" + song
    data = await get_api(final_link)
    if data["code"] == 404:
        return "未收录该歌曲，请检查后重试~"
    if singer == None:
        return [str(data["data"][0]["id"])]
    else:
        for i in data["data"]:
            if i["singer"] == singer:
                return [str(i["id"])]
        return "未找到该歌手的此首歌曲。"