from src.tools.dep.data_server import *
from src.tools.utils import *
from src.tools.dep.api.prompt import *
from src.tools.config import Config
_bot = Config.bot
_token = Config.jx3api_globaltoken


async def daily_(server: str = None, group_id: str = None, predict_day_num: int = 0):
    """
    获取日常图片链接
    @param predict_day_num 向后预测天数
    """
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    full_link = f"{Config.jx3api_link}/view/active/current?robot={_bot}&server={server}&num={predict_day_num}"
    data = await get_api(full_link)
    return data["data"]["url"]


class DailyResponse:
    mark = {
        'war': ['pve', '大战', 3701],
        'card': ['pve', '副本', 3601],
        'team': ['pve', '团队秘境', 3501],

        'leader': ['pvp', '世界BOSS', 2701],
        'battle': ['pvp', '战场', 2601],
        'orecar': ['pvp', '矿车',  2501],

        'draw': ['pvx', '美人图', 1701],
        'luck': ['pvx', '摸宠', 1601],
        'school': ['pvx', '门派', 1501],
        'rescue': ['pvx', '驰援', 1502],
    }

    def convert(self, field: str):
        x = self.data.get(field)
        if not x:
            return None
        if isinstance(x, list):
            x = str.join('\n', x)
        return x

    def load_data(self):
        result = []
        for key in self._data:
            item = DailyResponse.mark.get(key)
            if not item:
                continue
            result.append([self._data[key]] + item)
            # [今日数据 , 类型 , 子分类 , 排序]
        self.items = list(sorted(result, key=lambda x: x[3]))

    @property
    def text(self):
        result = [f'{self.date}的日常：']
        prev_type = None
        for x in self.items:
            data, cur_type, sub_title, rank = x
            if cur_type != prev_type:
                if prev_type is not None:
                    result.append('\n\n')
                result.append(f'- {cur_type}')
                prev_type = cur_type
            result.append(f'{sub_title}:{data}')
        return str.join('\n', result)

    def __init__(self, data: dict) -> None:
        self._data = data
        self.date = DateTime(data.get('date')).tostring(DateTime.Format.DEFAULT)
        self.data = self.load_data()


async def daily_txt(server: str = None, group_id: str = None, predict_day_num: int = 0):
    """
    获取日常
    @param predict_day_num 向后预测天数
    """
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    full_link = f"{Config.jx3api_link}/data/active/current?server={server}&num={predict_day_num}"
    data = await get_api(full_link)
    return DailyResponse(data).text
