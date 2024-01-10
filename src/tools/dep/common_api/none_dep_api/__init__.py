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
        'war': ['PVE', '大战', 3701, None],
        'card': ['PVE', '家园声望', 3601, None],
        'team': ['PVE', '武林通鉴', 3501, None],

        'leader': ['PVP', '世界BOSS', 2701, lambda x:[f'主线{x[0]}', f'分线{x[1]}']],
        'battle': ['PVP', '战场', 2601, None],
        'orecar': ['PVP', '阵营',  2501, None],

        'draw': ['PVX', '美人图', 1701, None],
        'luck': ['PVX', '摸宠', 1601, None],
        'school': ['PVX', '门派', 1501, None],
        'rescue': ['PVX', '驰援', 1502, None],
    }

    def load_data(self):
        result = []
        for key in self._data:
            item = DailyResponse.mark.get(key)
            if not item:
                continue
            x = self._data[key]
            if isinstance(x, list):
                x = str.join('\n\t', x)
            result.append([x] + item)
            # [今日数据 , 类型 , 子分类 , 排序]
        self.items = list(sorted(result, key=lambda x: x[3]))

    @property
    def text(self):
        result = [f'{self.date}的日常：']
        prev_type = None
        for x in self.items:
            data, cur_type, sub_title, rank, mapper = x
            if mapper: # 映射
                data = mapper(mapper)
            if cur_type != prev_type:
                if prev_type is not None:
                    result.append('')
                result.append(f'- {cur_type}')
                prev_type = cur_type
            result.append(f'{sub_title}：{data}')
        return str.join('\n', result)

    def __init__(self, data: dict) -> None:
        self._data = data.get('data') or {}
        self.date = DateTime(self._data.get('date')).tostring(DateTime.Format.YMD)
        self.load_data()

        if not self._data:
            return logger.warning(f'invalid data on daily:{data}')


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
    print(data)
    return DailyResponse(data).text
