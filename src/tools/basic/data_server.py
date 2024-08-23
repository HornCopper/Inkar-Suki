from typing import Optional

from src.tools.utils.path import TOOLS

from .group_opeator import getGroupSettings

import json

def Zone_mapping(server, legacy: bool = False) -> Optional[str]:
    if server in ["绝代天骄"]:
        return "电信区" if not legacy else "电信八区"
    if server in ["斗转星移", "唯我独尊", "乾坤一掷", "横刀断浪", "剑胆琴心", "幽月轮", "梦江南"]:
        return "电信区" if not legacy else "电信五区"
    if server in ["长安城", "蝶恋花", "龙争虎斗"]:
        return "电信区" if not legacy else "电信一区"
    if server in ["青梅煮酒"]:
        return "双线区" if not legacy else "双线四区"
    if server in ["破阵子", "天鹅坪"]:
        return "双线区" if not legacy else "双线一区"
    if server in ["飞龙在天"]:
        return "双线区" if not legacy else "双线二区"
    if server in ["英雄客", "自当狂", "九万里", "万象长安", "山海相逢", "有人赴约", "眉间雪"]:
        return "无界区"
    return None


def server_mapping(server: Optional[str] = "", group_id: Optional[str] = "") -> Optional[str]:
    with open(TOOLS + "/basic/server.json", mode="r", encoding="utf8") as servers_raw_data:
        servers = json.loads(servers_raw_data.read())
        """
        根据服务器别名匹配服务器，若未输入则获取当前群所绑定的服务器
        """
        if server:
            for i in list(servers):
                if server in servers[i]:
                    return i
        return getGroupServer(group_id=group_id)


def getGroupServer(group_id: Optional[str]) -> Optional[str]:
    """
    获取当前群所绑定的服务器，若未绑定则返回None
    """
    if not group_id:
        return None
    group = getGroupSettings(group_id, "server")
    if not isinstance(group, Optional[str]):
        return
    if not group:
        return None
    return group