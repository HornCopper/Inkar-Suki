from src.tools.utils import *
from ..GroupConfigInfo import *
groupConfigAuth: dict[str, GroupConfigInfo] = {
    'start': GroupConfigInfo('首次使用', default=DateTime('2024-01-08').timestamp()),
    'uses': GroupConfigInfo('使用记录', '记录每个授权区间', default=[]),
    'allow_server': GroupConfigInfo('可绑区服', '若无内容，则可任意绑定', default=[]),
    'allow_bot': GroupConfigInfo('可绑机器人', '若无内容，则可任意绑定', default=[]),
}

groupConfigInfos: dict[str, GroupConfigInfo] = {
    'auth': GroupConfigInfo('授权', default={}, infos=groupConfigAuth),
    'server': GroupConfigInfo('当前绑定服务器'),
    'bot': GroupConfigInfo('当前机器人'),
    'subscribe': GroupConfigInfo('当前订阅的事件', default={'日常': {}}),
}
