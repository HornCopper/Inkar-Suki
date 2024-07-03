from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=1101)
class GranaryRobbedRecvEvent(RecvEvent):
    """粮仓被劫事件"""

    __event__ = "WsRecv.GranaryRobbed"
    message_type: str = "GranaryRobbed"
    server: str
    """服务器名称"""
    castle: str
    """据点名称"""
    camp_name: str
    """阵营名称"""

    @property
    def log(self) -> str:
        log = f"{self.server} 的 {self.castle} 据点粮仓被一群 {self.camp_name} 人士洗劫，损失一半据点资金。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        msg = f"{self.server} 的 {self.castle} 据点粮仓被一群 {self.camp_name} 人士洗劫，损失一半据点资金。"
        return {"type": "战况", "msg": msg, "server": self.server}

@EventRister.rister(action=1102)
class LeaderResetRecvEvent(RecvEvent):
    """大将重置事件"""

    __event__ = "WsRecv.LeaderReset"
    message_type: str = "LeaderReset"
    server: str
    """服务器名称"""
    name: str
    """据点名称"""

    @property
    def log(self) -> str:
        log = f"{self.server} 的 {self.name} 据点大旗长时间无人守护，被据点大将重置回初始位置！"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        msg = f"{self.server} 的 {self.name} 据点大旗长时间无人守护，被据点大将重置回初始位置！"
        return {"type": "战况", "msg": msg, "server": self.server}


@EventRister.rister(action=1103)
class FlagRobbedRecvEvent(RecvEvent):
    """大旗被夺事件"""

    __event__ = "WsRecv.FlagRobbed"
    message_type: str = "FlagRobbed"
    server: str
    """服务器名称"""
    camp_name: str
    """阵营名称"""
    map_name: str
    """地图名称"""
    castle: str
    """据点名称"""

    @property
    def log(self) -> str:
        log = f"{self.server} 的 {self.camp_name} 位于 {self.map_name} 的 {self.castle} 据点大旗被夺，10分钟后若未能夺回大旗，则会丢失此据点！"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        msg = f"{self.server} 的 {self.camp_name} 位于 {self.map_name} 的 {self.castle} 据点大旗被夺，10分钟后若未能夺回大旗，则会丢失此据点！"
        return {"type": "战况", "msg": msg, "server": self.server}

@EventRister.rister(action=1104)
class TongCastleRobbedRecvEvent(RecvEvent):
    """据点占领事件(有帮会)"""

    __event__ = "WsRecv.TongCastleRobbed"
    message_type: str = "TongCastleRobbed"
    server: str
    """服务器名称"""
    camp_name: str
    """阵营名称"""
    tong_name: str
    """帮会名称"""
    castle: str
    """据点名称"""

    @property
    def log(self) -> str:
        log = f"{self.server} 的 {self.camp_name} 的【{self.tong_name}】帮会成功占领【{self.castle}】据点！"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        msg = f"{self.server} 的 {self.camp_name} 的【{self.tong_name}】帮会成功占领【{self.castle}】据点！"
        return {"type": "战况", "msg": msg, "server": self.server}

@EventRister.rister(action=1105)
class CastleRobbedRecvEvent(RecvEvent):
    """据点占领事件(无帮会)"""

    __event__ = "WsRecv.CastleRobbed"
    message_type: str = "CastleRobbed"
    server: str
    """服务器名称"""
    camp_name: str
    """阵营名称"""
    castle: str
    """据点名称"""

    @property
    def log(self) -> str:
        log = f"{self.server} 的 {self.camp_name} 成功占领【{self.castle}】据点！参与帮会均拥有据点，故此据点归属于{self.camp_name}，本阵营无据点的帮会可前来挑战守将获得拥有权。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        msg = f"{self.server} 的 {self.camp_name} 成功占领【{self.castle}】据点！参与帮会均拥有据点，故此据点归属于{self.camp_name}，本阵营无据点的帮会可前来挑战守将获得拥有权。"
        return {"type": "战况", "msg": msg, "server": self.server}

@EventRister.rister(action=1106)
class SettlementRecvEvent(RecvEvent):
    """战况结算事件"""

    __event__ = "WsRecv.Settlement"
    message_type: str = "Settlement"
    server: str
    """服务器名称"""
    camp_name: str
    """阵营名称"""
    tong_list: list
    """帮会列表"""

    @property
    def log(self) -> str:
        tongs = "【" + "】、【".join(self.tong_list) + "】"
        log = f"{self.server} 的逐鹿中原活动结束，本次{self.camp_name}贡献前五十的开战据点帮会和贡献前五的非开战据点帮会：{tongs}。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        tongs = "【" + "】、【".join(self.tong_list) + "】"
        msg = f"{self.server} 的逐鹿中原活动结束，本次{self.camp_name}贡献前五十的开战据点帮会和贡献前五的非开战据点帮会：{tongs}。"
        return {"type": "战况", "msg": msg, "server": self.server}