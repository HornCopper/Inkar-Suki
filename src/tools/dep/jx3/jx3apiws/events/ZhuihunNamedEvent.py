from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=1008)
class ZhuihunNamedEvent(RecvEvent):
    """游戏系统频道消息推送"""

    __event__ = "WsRecv.ZhuihunNamedMsg"
    message_type = "ZhuihunNamed"
    zone: str
    """游戏大区"""
    server: str
    """游戏服务器"""
    subserver: str
    """原始服务器"""
    name: str
    """角色名称"""
    realm: str
    """目标服务器"""
    time: int
    """时间"""

    @property
    def log(self) -> str:
        log = f"追魂点名：先锋队执事：请[{self.subserver}·{self.name}]侠士速来[{self.realm}]·跨服烂柯山，有要事相商！。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        origin_s = self.subserver
        origin_n = self.name
        goal_s = self.realm
        final_template = f"先锋队执事：请[{origin_n}·{origin_s}]侠士速来[{goal_s}]·跨服烂柯山，有要事相商！"
        return {"type":"追魂", "server": self.server, "msg": final_template}
