import nonebot
import sys
import re
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
from utils import get_api

def clean(string: str) -> str:
    return re.sub(r"§.", "", string)
async def jes(ip: str) -> str:
    ip = ip.split(":")
    if len(ip) > 2:
        return "唔……暂时无法识别IPv6地址，或者是您的地址输入有误哦~"
    elif len(ip) == 2:
        port = ip[1]
        ip = ip[0]
    else:
        ip = ip[0]
        port = 25565
    try:
        final_link = f"http://motd.wd-api.com/v1/java?host={ip}&platform={port}"
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
        desc = ""
        for i in infomation["description"]["extra"]:
            desc = desc + clean(i["text"])
        maxp = infomation["players"]["max"]
        onlp = infomation["players"]["online"]
        return f"已经查到Java版服务器啦：\n地址：{ip}:{port}\n在线人数：{onlp}/{maxp}\n介绍：{desc}"
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
            return "唔……域名解析失败。"
        else:
            return "唔……未知错误。"
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