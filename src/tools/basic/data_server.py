from src.tools.basic import *
from .group_opeator import getGroupData

import json

def Zone_mapping(server):
    if server in {"绝代天骄"}:
        return "电信八区"
    if server in {"斗转星移", "唯我独尊", "乾坤一掷", "横刀断浪", "剑胆琴心", "幽月轮", "梦江南"}:
        return "电信五区"
    if server in {"长安城", "蝶恋花", "龙争虎斗"}:
        return "电信一区"
    if server in {"青梅煮酒"}:
        return "双线四区"
    if server in {"破阵子", "天鹅坪"}:
        return "双线一区"
    return None

servers = json.loads(read(TOOLS + "/basic/server.json"))

def server_mapping(server: str = None, group_id: str = None):
    """
    根据服务器别名匹配服务器，若未输入则获取当前群所绑定的服务器
    """
    if server:
        for i in list(servers):
            if server in servers[i]:
                return i
    return getGroupServer(group_id=group_id)


def getGroupServer(group_id: str):
    """
    获取当前群所绑定的服务器，若未绑定则返回None
    """
    if not group_id:
        return None
    group = getGroupData(group_id, "server")
    if not group:
        return None
    return group