from src.tools.utils import *
from ..GroupConfigInfo import *
groupConfigAuth: dict[str, GroupConfigInfo] = {
    'start': GroupConfigInfo('首次使用', default=DateTime('2024-01-08').timestamp()),
    'uses': GroupConfigInfo('使用记录', '记录每个授权区间', default=[]),
    'allow_server': GroupConfigInfo('可绑区服', '若无内容，则可任意绑定', default=[]),
    'allow_bot': GroupConfigInfo('可绑机器人', '若无内容，则可任意绑定', default=[]),
}
groupConfigActivity: dict[str, GroupConfigInfo] = {
    'general': GroupConfigInfo('常规消息数', default=[0]*31, description='单个数组循环存储1月内消息数'),
    'command': GroupConfigInfo('功能使用数', default=[0]*31, description='单个数组循环存储1月内消息数'),
    'slient_count': GroupConfigInfo('沉寂天数', default=0, description='连续T日（默认7）功能使用数为X及以下（默认0）'),
}
groupConfigInfos: dict[str, GroupConfigInfo] = {
    'auth': GroupConfigInfo('授权', default={}, infos=groupConfigAuth),
    'server': GroupConfigInfo('当前绑定服务器'),
    'bot': GroupConfigInfo('当前机器人'),
    'subscribe': GroupConfigInfo('当前订阅的事件', default={'日常': {}}),
    'activity': GroupConfigInfo('活跃度', default={}, infos=groupConfigActivity),
    'command_map': GroupConfigInfo('命令映射', default={}),
}
