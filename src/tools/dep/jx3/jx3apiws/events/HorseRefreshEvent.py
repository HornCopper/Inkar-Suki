from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=1002)
class HorseRefreshEvent(RecvEvent):
    """马驹刷新事件"""

    __event__ = "WsRecv.HorseRefresh"
    message_type = "HorseRefresh"
    zone: str
    """游戏大区"""
    server: str
    """服务器"""
    map_name: str
    """刷新地图"""
    min_time: int
    """时间范围min"""
    max_time: int
    """时间范围max"""
    time: int
    """推送时间"""

    @property
    def log(self) -> str:
        log = f"马驹刷新推送：{self.server}的 {self.map_name}即将在 {str(self.min_time)}-{str(self.max_time)} 分钟后刷新马驹，请有意愿的侠士速去捕捉！"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return {"type": "抓马", "server": self.server, "msg": f"{self.server}的{self.map_name}将在{str(self.min_time)}-{str(self.max_time)}刷新马驹哦~"}


@EventRister.rister(action=1003)
class HorseCaughtEvent(RecvEvent):
    """马驹捕获事件"""

    __event__ = "WsRecv.HorseCaught"
    message_type = "HorseCaught"
    
    zone: str
    """游戏大区"""
    server: str
    """服务器"""
    name: str
    """捕获角色"""
    horse: str
    """马驹名称"""
    map_name: str
    """捕获地点"""
    time: int
    """捕获时间"""
    
    @property
    def log(self) -> str:
        final_time = convert_time(self.time, "%H:%M")
        log = f"马驹捕获推送：[{self.server}]的{self.horse}于{final_time}在{self.map_name}被{self.name}捕获了！"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        final_time = convert_time(self.time, "%H:%M")
        return {"type": "抓马", "server": self.server, "msg": f"{self.server} 的 {self.horse} 于 {final_time} 在 {self.map_name} 被[{self.name}]捕获了！"}

@EventRister.rister(action=1010)
class DiluRefreshEvent(RecvEvent):
    """的卢刷新事件"""

    __event__ = "WsRecv.DiluRefresh"
    message_type = "DiluRefresh"
    zone: str
    """游戏大区"""
    server: str
    """服务器"""
    name: str
    """刷新名称（的卢）"""
    time: int
    """时间戳"""

    @property
    def log(self) -> str:
        final_time = convert_time(self.time, "%H:%M")
        log = f"的卢刷新推送：{self.server}的{self.name}即将在{final_time}左右刷新！"
        return log
    
    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return {"type": "的卢", "server": self.server, "msg": f"{self.server} 的{self.name}即将刷新！"}
    
@EventRister.rister(action=1011)
class DiluAppearEvent(RecvEvent):
    """的卢事件"""

    __event__ = "WsRecv.DiluAppear"
    message_type = "DiluAppear"
    zone: str
    """游戏大区"""
    server: str
    """服务器"""
    map_name: str
    """地图名称"""
    name: str
    """刷新名称（的卢）"""
    time: int
    """时间戳"""

    @property
    def log(self) -> str:
        final_time = convert_time(self.time, "%H:%M")
        log = f"的卢出现推送：{self.server}的{self.name}于{final_time}出现在了{self.map_name}！"
        return log
    
    @overrides(RecvEvent)
    def get_message(self) -> dict:
        final_time = convert_time(self.time, "%H:%M")
        return {"type": "的卢", "server": self.server, "msg": f"{self.server} 的{self.name}于 {final_time} 出现在 {self.map_name}，请浩气盟和恶人谷的侠士速去捕捉！"}
    
@EventRister.rister(action=1012)
class DiluRefreshEvent(RecvEvent):
    """的卢刷新事件"""

    __event__ = "WsRecv.DiluCaught"
    message_type = "DiluCaught"
    zone: str
    """游戏大区"""
    server: str
    """服务器"""
    role_name: str
    """捕获者"""
    camp_name: str
    """捕获阵营"""
    map_name: str
    """捕获地图"""
    name: str
    """刷新名称（的卢）"""
    time: int
    """时间戳"""

    @property
    def log(self) -> str:
        final_time = convert_time(self.time, "%H:%M")
        log = f"的卢捕获推送：{self.server}的{self.name}在{self.map_name}被{self.camp_name}的{self.role_name}于{final_time}捕获了！"
        return log
    
    @overrides(RecvEvent)
    def get_message(self) -> dict:
        final_time = convert_time(self.time, "%H:%M")
        return {"type": "的卢", "server": self.server, "msg": f"{self.server} 的{self.name}在 {self.map_name} 被 {self.camp_name}的[{self.role_name}]于 {final_time} 捕获了！"}

@EventRister.rister(action=1013)
class DiluSoldEvent(RecvEvent):
    """的卢事件"""

    __event__ = "WsRecv.DiluSold"
    message_type = "DiluSold"
    zone: str
    """游戏大区"""
    server: str
    """服务器"""
    role_name: str
    """买家"""
    camp_name: str
    """买家阵营"""
    amount: str
    """价格"""
    name: str
    """刷新名称（的卢）"""
    time: int
    """时间戳"""

    @property
    def log(self) -> str:
        final_time = convert_time(self.time, "%H:%M")
        log = f"的卢竞拍推送：{self.server}的{self.name}于{final_time}被{self.camp_name}的{self.role_name}以{self.amount}的价格竞拍成功！"
        return log
    
    @overrides(RecvEvent)
    def get_message(self) -> dict:
        final_time = convert_time(self.time, "%H:%M")
        return {"type": "的卢", "server": self.server, "msg": f"{self.server} 的{self.name}于 {final_time} 被 {self.camp_name}的[{self.role_name}]以 {self.amount} 的价格竞拍成功！"}