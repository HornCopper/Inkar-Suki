
from enum import Enum
import json
from src.tools.utils import get_api
from src.tools.file import write, read
from sgtpyutils.extensions.clazz import dict2obj
import nonebot
import pathlib2
TOOLS = nonebot.get_driver().config.tools_path
ASSETS = pathlib2.Path(TOOLS).parent.joinpath("assets").__str__()


async def check_bind(id: str):
    final_url = f"https://helper.jx3box.com/api/wiki/post?type=item&source_id={id}"
    data = await get_api(final_url)
    bind_type = data["data"]["source"]["BindType"] or 0
    return bind_type

GoodsBindTypeBindTypes = ["未知", "不绑定", "装备后绑定", "拾取后绑定"]


class GoodsBindType(Enum):

    UnKnown = 0
    UnBind = 1
    BindOnUse = 2
    BindOnPick = 3


class GoodsInfo(dict):
    def __init__(self, data: dict = None) -> None:
        if data is None:
            data = {}
        self.id = data.get('id')
        self._bind_type: GoodsBindType = GoodsBindType.BindOnPick
        self.bind_type = data.get('bind_type')
        self.icon = data.get('IconID') or 18888  # 默认给个小兔兔
        self.quality = data.get('Quality')
        self.ui_id = data.get('UiID')
        self.name = data.get('Name') or '未知物品'
        '''被使用的次数，次数多的优先前置'''
        self.u_popularity = 0
        super().__init__()

    @property
    def bind_type(self) -> GoodsBindType:
        if isinstance(self._bind_type, GoodsBindType):
            return self._bind_type
        self._bind_type = GoodsBindType(self._bind_type)
        return self._bind_type

    @bind_type.setter
    def bind_type(self, v: GoodsBindType):
        if v is None:
            self._bind_type = GoodsBindType.BindOnPick  # default
            return
        self._bind_type = v

    @property
    def img_url(self):
        return f"https://icon.jx3box.com/icon/{self.icon}.png"

    @property
    def html_code(self):
        return f"<img src={self.img_url}></img>"

    @property
    def color(self):
        '''
        根据品质返回 老灰、灰、绿、蓝、紫、金、红
        '''
        return ['rgb(220,220,220)', 'rgb(190,190,190)', 'rgb(0, 210, 75)', 'rgb(0, 126, 255)', 'rgb(254, 45, 254)', 'rgb(255, 165, 0)', '#ff0000'][self.quality]

    def to_row(self):
        new = [self.id, self.name, self.bind_type_str, self.html_code]
        return new

    @property
    def bind_type_str(self):
        return GoodsBindTypeBindTypes[self.bind_type.value]

    def __repr__(self) -> str:
        return json.dumps(self.__dict__)


cache_file = ASSETS + "/jx3/info_tradegoods.json"
CACHE_goods = json.loads(read(cache_file))  # 每次重启后从磁盘加载缓存
CACHE_goods = dict([[x, dict2obj(GoodsInfo(), CACHE_goods[x])]
                   for x in CACHE_goods])  # 转换为类


class GoodsEncoder(json.JSONEncoder):
    def default(self, o) -> str:
        if isinstance(o, Enum):
            return o.value
        return super().default(o)


def flush_cache_goods():
    data = json.dumps(dict([key, CACHE_goods[key].__dict__]
                      for key in CACHE_goods), cls=GoodsEncoder)
    write(cache_file, data)
