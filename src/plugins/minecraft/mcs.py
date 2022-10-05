import nonebot
import sys
import re
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
from utils import get_api

def clean(string: str) -> str:
    return re.sub(r"§.", "", string)

async def jes(ip: str):
    ip_string = ip.split(":")
    if len(ip_string) not in [1,2]:
        return "唔……输入的IP地址有误，请检查后重试~"
    if len(ip_string) == 1:
        ip = ip_string[0]
        port = 25565
    else:
        ip = ip_string[0]
        port = ip_string[1]
    final_url = f"https://motd.wd-api.com/v1/java?host={ip}&port={port}"
    data = await get_api(final_url)
    if "message" in list(data):
        if data["message"].find("ECONNREFUSED") != -1:
            return "唔……MC服务器拒绝了我们的连接请求。"
        elif data["message"].find("ENOTFOUND") != -1:
            return "唔……域名解析失败，请检查后重试~"
        else:
            return "唔……未知错误。"
    else:
        name_1 = clean(data["version"]["name"])
        name_2 = ""
        for i in data["description"]["extra"]:
            name_2 = name_2 + i["text"]
        name_2 = clean(name_2)
        online = data["players"]["online"]
        max = data["players"]["max"]
        people_count = f"{online}/{max}"
        return f"已经查到Java版服务器啦！\n地址：{ip}:{port}\n在线人数：{people_count}\n介绍：{name_1} - {name_2}"
    
async def bes(ip: str) -> str:
    ip = ip.split(":")
    if len(ip) > 2:
        return "唔……暂时无法识别IPv6地址，或者是您的地址输入有误哦~"
    elif len(ip) == 2:
        port = ip[1]
        ip = ip[0]
    else:
        ip = ip[0]
        port = 19132
    try:
        final_link = f"http://motd.wd-api.com/v1/bedrock?host={ip}&platform={port}"
        infomation = await get_api(final_link)
    except:
        return "唔……获取信息失败：连接API超时。"
    try:
        error = infomation["message"]
        if error.find("getaddrinfo ENOTFOUND") != -1:
            return "唔……获取信息失败：DNS出错，域名尚未绑定该IP地址。"
        else:
            return "唔……获取信息失败：未知错误。"
    except:
        unpack_data = infomation["data"].split(";")
        motd_1 = clean(unpack_data[1])
        motd_2 = clean(unpack_data[7])
        player_count = unpack_data[4]
        max_players = unpack_data[5]
        edition = unpack_data[0]
        version_name = unpack_data[3]
        game_mode = unpack_data[8]
        if game_mode == "Survival":
            game_mode = "生存"
        elif game_mode == "Creative":
            game_mode = "创造"
        elif game_mode == "Adventure":
            game_mode = "冒险"
        else:
            game_mode = "未知"
        return f"已经查到基岩版服务器啦：\n地址：{ip}:{port}\n在线人数：{player_count}/{max_players}\n版本：{edition}{version_name}\n游戏模式：{game_mode}\n介绍：{motd_1} - {motd_2}"