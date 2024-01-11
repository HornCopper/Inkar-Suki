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
    # mark = {
    #     'war': ['日常', '秘境大战', 3701, None],
    #     'battle': ['日常', '今日战场', 3601, None],
    #     'school': ['日常', '宗门事件', 3501, None],
    #     'orecar': ['日常', '阵营任务',  3401, None],
    #     'leader': ['日常', '世界首领', 3301, lambda data:f'主:{data[0]}/分:{data[1]}' if isinstance(data, list) else data],
    #     'draw': ['日常', '美人画像', 3201, None],
    #     'luck': ['日常', '福源宠物', 3101, None],
    #     'rescue': ['日常', '驰援任务', 3001, None],

    #     'card': ['周常', '家园声望·加倍道具', 2501, None],
    #     'team': ['周常', '', 2401, lambda data:[
    #         f'\n【武林通鉴·公共任务】\n{data[0]}',
    #         f'\n【武林通鉴·秘境任务】\n{data[1]}',
    #         f'\n【武林通鉴·团队秘境】\n{data[2]}',
    #     ]],
    # }
    mark = {
        'war': ['日常', '大战', 3701, None],
        'battle': ['日常', '战场', 3601, None],
        'school': ['日常', '宗门', 3501, None],
        'orecar': ['日常', '阵营',  3401, None],
        'leader': ['日常', '世界', 3301, lambda data:f'主:{data[0]}/分:{data[1]}' if isinstance(data, list) else data],
        'draw': ['日常', '画像', 3201, None],
        'luck': ['日常', '福缘', 3101, None],
        'rescue': ['日常', '驰援', 3001, None],

        'card': ['周常', '【家园声望·加倍道具】\n', 2501, None],
        'team': ['周常', '', 2401, lambda data:[
            f'【武林通鉴·公共任务】\n{data[0]}',
            f'\n【武林通鉴·秘境任务】\n{data[1]}',
            f'\n【武林通鉴·团队秘境】\n{data[2]}',
        ]],
    }

    def load_data(self):
        result = []
        for key in self._data:
            item = DailyResponse.mark.get(key)
            if not item:
                continue
            mapper = item[3]
            x = self._data[key]
            if mapper:  # 映射
                x = mapper(x)
            if isinstance(x, list):
                x = str.join(',', x)
            result.append([x] + item)
            # [今日数据 , 类型 , 子分类 , 排序]
        self.items = list(sorted(result, key=lambda x: -x[3]))

    @property
    def text(self):
        date = self.date.tostring('%m月%d日')
        weekday = f'星期{["一","二","三","四","五","六","天"][self.date.weekday()]}'
        result = [f'{self.server}{date}{weekday}']
        prev_type = None
        for x in self.items:
            data, cur_type, sub_title, rank, mapper = x
            if cur_type != prev_type:
                if prev_type is not None:
                    result.append('')
                # result.append(f'- {cur_type}')
                prev_type = cur_type
            prefix = '' if not sub_title else (
                sub_title if sub_title[-1] == '\n' else f'{sub_title}：')
            result.append(f'{prefix}{data}')
        return str.join('\n', result)

    def __init__(self, server: str, data: dict) -> None:
        self.server = server
        self._data = data.get('data') or {}
        self.date = DateTime(self._data.get('date'))
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
    return DailyResponse(server, data)
