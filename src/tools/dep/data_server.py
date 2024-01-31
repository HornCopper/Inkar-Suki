from src.tools.file import *
from src.tools.utils import *
import json
from .bot.group_env import *
from src.constant.jx3 import *
server_raw_map = {
    "幽月轮": ["二合一", "四合一", "六合一", "七合一", "千岛湖", "圣墓山", "执子之手", "平步青云", "笑傲江湖", "幽月轮", "山雨欲来", "幽"],
    "剑胆琴心": ["剑胆琴心", "煎蛋", "剑胆", "琴", "琴心", "剑"],
    "梦江南": ["梦江南", "双梦", "如梦令", "枫泾古镇", "双梦镇", "梦"],
    "斗转星移": ["斗转星移", "金戈铁马", "风雨同舟", "大唐万象", "姨妈", "风雨", "风雨大姨妈", "斗", "姨"],
    "长安城": ["长安城", "长安", "长"],
    "绝代天骄": ["电八", "电信八区", "绝代天骄", "风骨霸刀", "绝代双骄", "绝代", "绝"],
    "龙争虎斗": ["龙虎", "龙争虎斗", "龙"],
    "唯我独尊": ["唯满侠", "唯我独尊", "wmx", "唯我", "WMX", "唯"],
    "乾坤一掷": ["华山论剑", "乾坤一掷", "花钱", "华乾", "乾"],
    "蝶恋花": ["蝶服", "蝶恋花", "蝶"],
    "天鹅坪": ["纵月", "天鹅坪", "天鹅", "天"],
    "青梅煮酒": ["青梅煮酒", "青梅", "青"],
    "横刀断浪": ["横刀断浪", "横刀", "横"],
    "破阵子": ["破阵子", "念破", "破"],
    "飞龙在天": ["飞龙在天", "飞龙", "飞"],
}
server_map = {}
for x in server_raw_map:
    for srv in server_raw_map[x]:
        server_map[srv] = x
    server_map[x] = x  # 绑定自身


def Zone_mapping(server):
    """obsolete"""
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
    logger.warning("fail to found server zone:{server}")
    return None


def server_mapping(server: str = None, group_id: str = None):
    """
    根据服务器别名匹配服务器，若未输入则获取当前群所绑定的服务器
    """
    if server:
        server: Server = Server.from_alias(server, log=False)
        if server:
            return server.name
    return getGroupServer(group_id=group_id)


def getGroupServer(group_id: str):
    """
    获取当前群所绑定的服务器，若未绑定则返回None
    """
    if not group_id:
        return None
    data = GroupConfig(group_id, log=False)
    return data.mgr_property("server")
