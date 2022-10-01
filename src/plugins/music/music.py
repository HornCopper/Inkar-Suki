import nonebot
import sys

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from utils import get_api

async def search(platform_: str, song: str):
    '''
    搜索型函数。

    返回搜索结果。

    第一个参数是平台，类型为`str`，自动判断。
    '''
    if platform_ in ["QQ","QQ音乐","qq","q","Q","tx","tc","tencent","腾讯","腾讯音乐","qq音乐","Qq","Qq音乐","qQ","qQ音乐"]:
        platform = 1 # 1 QQ 2 网易
    elif platform_ in ["网易","163","网抑云","网抑","网","netease","n","网易云音乐","网抑云音乐","网易云","wy","w"]:
        platform = 2
    else:
        platform = 1
    keyword = song
    if platform == 1:
        api = "https://c.y.qq.com/splcloud/fcgi-bin/smartbox_new.fcg?format=json&key=" + keyword
        data = await get_api(url = api)
        id = []
        song_ = []
        for i in data["data"]["song"]["itemlist"]:
            song_name = i["name"] + " - " + i["singer"]
            song_.append(song_name)
            id.append(i["id"])
        if len(id) == 0:
            return "404"
        return [song_, id, platform]
    elif platform == 2:
        api = "https://music.163.com/api/cloudsearch/pc?type=1&offset=1&s=" + keyword
        data = await get_api(url = api)
        id = []
        song_ = []
        for i in data["result"]["songs"]:
            id.append(i["id"])
            song_name = i["name"] + " - " + i["ar"][0]["name"]
            song_.append(song_name)
        if len(id) == 0:
            return "404"
        return [song_, id, platform]

async def get(platform_: str, song: str, singer: str = None):
    '''
    请求型函数。

    不经过选择直接推送。

    第一个参数是平台，类型为`str`，自动判断。
    '''
    if platform_ in ["QQ","QQ音乐","qq","q","Q","tx","tc","tencent","腾讯","腾讯音乐","qq音乐","Qq","Qq音乐","qQ","qQ音乐"]:
        platform = 1 # 1 QQ 2 网易
    elif platform_ in ["网易","163","网抑云","网抑","网","netease","n","网易云音乐","网抑云音乐","网易云","w","wy"]:
        platform = 2
    else:
        platform = 1
    keyword = song
    if platform == 1:
        api = "https://c.y.qq.com/splcloud/fcgi-bin/smartbox_new.fcg?format=json&key=" + keyword
        data = await get_api(url = api)
        if len(data["data"]["song"]) == 0:
            return "404"
        if singer == None:
            song_name = data["data"]["song"]["itemlist"][0]["name"] + " - " + data["data"]["song"]["itemlist"][0]["singer"]
            id = data["data"]["song"]["itemlist"][0]["id"]
            return [song_name, id, platform]
        else:
            for i in data["data"]["song"]["itemlist"]:
                if i["singer"] == singer:
                    song_name = i["name"] + " - " + i["singer"]
                    id = i["id"]
                    return [song_name, id, platform]
            return "404"
    elif platform == 2:
        api = "https://music.163.com/api/cloudsearch/pc?type=1&offset=1&s=" + keyword
        data = await get_api(url = api)
        if len(data["result"]["songs"]) == 0:
            return "404"
        if singer == None:
            song_name = data["result"]["songs"][0]["name"] + " - " + data["result"]["songs"][0]["ar"][0]["name"]
            id = data["result"]["songs"][0]["id"]
            return [song_name, id, platform]
        else:
            for i in data["result"]["songs"]:
                if i["ar"][0]["name"] == singer:
                    song_name = i["name"] + " - " + i["ar"][0]["name"]
                    id = i["id"]
                    return [song_name, id, platform]
            return "404"