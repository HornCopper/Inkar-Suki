from src.tools.file import read
from src.tools.dep.path import DATA
import json
__map = {
    "幽月轮": ["二合一", "四合一", "六合一", "七合一", "千岛湖", "圣墓山", "执子之手", "平步青云", "笑傲江湖", "幽月轮", "山雨欲来"],
    "剑胆琴心": ["剑胆琴心", "煎蛋", "剑胆"],
    "梦江南": ["梦江南", "双梦", "如梦令", "枫泾古镇", "双梦镇"],
    "斗转星移": ["斗转星移", "金戈铁马", "风雨同舟", "大唐万象", "姨妈", "风雨", "风雨大姨妈"],
    "长安城": ["长安城"],
    "绝代天骄": ["电八", "电信八区", "绝代天骄", "风骨霸刀", "绝代双骄"],
    "龙争虎斗": ["龙虎", "龙争虎斗"],
    "唯我独尊": ["唯满侠", "唯我独尊", "wmx", "唯我", "WMX"],
    "乾坤一掷": ["华山论剑", "乾坤一掷", "花钱", "华乾"],
    "蝶恋花": ["蝶服", "蝶恋花"],
    "天鹅坪": ["纵月", "天鹅坪"],
    "青梅煮酒": ["青梅煮酒", "青梅"],
    "横刀断浪": ["横刀断浪", "横刀"],
    "破阵子": ["破阵子", "念破"],
    "飞龙在天": ["飞龙在天", "飞龙"],
}
server_map = {}
for x in __map:
    for srv in __map[x]:
        server_map[srv] = x


def server_mapping(server: str = None, group_id: str = None):
    '''
    根据服务器别名匹配服务器，若未输入则获取当前群所绑定的服务器
    '''
    return server_map.get(server, getGroupServer(group_id=group_id))


def getGroupServer(group_id: str):
    '''
    获取当前群所绑定的服务器，若未绑定则返回None
    '''
    data = json.loads(read(f"{DATA}/{group_id}/jx3group.json"))
    data = data or {}
    return data.get('server', None)
