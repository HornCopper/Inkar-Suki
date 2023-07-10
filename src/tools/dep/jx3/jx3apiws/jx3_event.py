from abc import abstractmethod
from datetime import datetime
from typing import Literal, Optional

from nonebot.adapters import Event as BaseEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.typing import overrides
from nonebot.utils import escape_tag
from pydantic import BaseModel, Extra, validator

import json
import nonebot
import sys

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
ASSETS = TOOLS[:-5] + "assets"

from src.tools.file import *

'''
感谢友情提供代码@白师傅
原链接：
https://github.com/JustUndertaker/mini_jx3_bot
'''

class EventRister:
    """事件注册器"""

    event_dict: dict[int, "RecvEvent"] = {}
    """事件映射字典"""

    @classmethod
    def rister(cls, action: int):
        def _rister(event: "RecvEvent"):
            cls.event_dict[action] = event
            return event

        return _rister

    @classmethod
    def get_event(cls, ws_data: "WsData") -> Optional["RecvEvent"]:
        event = cls.event_dict.get(ws_data.action)
        if event:
            return event.parse_obj(ws_data.data)
        return None


class WsData(BaseModel):
    """
    ws数据模型
    """

    action: int
    """ws消息类型"""
    data: dict
    """消息数据"""


class WsNotice(BaseEvent):
    """ws通知主人事件"""

    __event__ = "WsNotice"
    post_type: str = "WsNotice"
    message: str
    """通知内容"""

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return self.post_type

    @overrides(BaseEvent)
    def get_event_name(self) -> str:
        return self.post_type

    @overrides(BaseEvent)
    def get_event_description(self) -> str:
        return escape_tag(str(self.dict()))

    @overrides(BaseEvent)
    def get_message(self) -> dict:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_plaintext(self) -> str:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_user_id(self) -> str:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_session_id(self) -> str:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def is_tome(self) -> bool:
        return False


class RecvEvent(BaseEvent, extra=Extra.ignore):
    """ws推送事件"""

    __event__ = "WsRecv"
    post_type: str = "WsRecv"
    message_type: str
    server: Optional[str] = None
    """影响服务器"""

    @property
    @abstractmethod
    def log(self) -> str:
        """事件日志内容"""
        raise NotImplementedError

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return self.post_type

    @overrides(BaseEvent)
    def get_event_name(self) -> str:
        message_type = getattr(self, "message_type", None)
        return f"{self.post_type}" + (f".{message_type}" if message_type else "")

    @overrides(BaseEvent)
    def get_event_description(self) -> str:
        return escape_tag(str(self.dict()))

    @overrides(BaseEvent)
    def get_message(self) -> dict:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_plaintext(self) -> str:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_user_id(self) -> str:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_session_id(self) -> str:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def is_tome(self) -> bool:
        return False


@EventRister.rister(action=2001)
class ServerStatusEvent(RecvEvent):
    """服务器状态推送事件"""

    __event__ = "WsRecv.ServerStatus"
    message_type = "ServerStatus"
    status: bool
    """服务器状态"""

    @validator("status", pre=True)
    def check_status(cls, v):
        return v == 1

    @property
    def log(self) -> str:
        status = "已开服" if self.status else "已维护"
        log = f"开服推送事件：[{self.server}]状态-{status}"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        time_now = datetime.now().strftime("%H:%M")
        if self.status:
            return {"type":"开服","server":self.server,"msg":f"{time_now} {self.server} 开服 (/≧▽≦)/"}
        elif self.status == False:
            return {"type":"开服","server":self.server,"msg":f"{time_now}：{self.server} 维护 ヘ(~ω~ヘ) "}


@EventRister.rister(action=2002)
class NewsRecvEvent(RecvEvent):
    """新闻推送事件"""

    __event__ = "WsRecv.News"
    message_type = "News"
    type: str
    """新闻类型"""
    title: str
    """新闻标题"""
    url: str
    """新闻url链接"""
    date: str
    """新闻日期"""

    @property
    def log(self) -> str:
        log = f"{self.type}事件：{self.title}"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return {"type":"公告","msg":f"{self.type}来啦！\n标题：{self.title}\n链接：{self.url}\n日期：{self.date}"}

@EventRister.rister(action=2003)
class ClientUpdateRecEvent(RecvEvent):
    """更新推送事件"""

    __event__ = "WsRecv.ClientUpdate"
    message_type = "ClientUpdate"
    old_version: str
    """旧版本"""
    new_version: str
    """新版本"""
    package_num: int
    """更新包数量"""
    package_size: str
    """更新包大小"""

    @property
    def log(self) -> str:
        log = f"客户端版本更新事件，更新至：{self.new_version}"
        return log
    
    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return {"type":"更新","msg":f"检测到客户端有更新哦~\n当前版本：{self.old_version}\n更新版本：{self.new_version}\n共计{self.package_num}个更新包，总大小为{self.package_size}。"}

@EventRister.rister(action=2004)
class SpillTheTeaEvent(RecvEvent):
    """818推送事件"""

    __event__ = "WsRecv.SpillTheTea"
    message_type = "SpillTheTea"
    server: str
    """服务器名"""
    name: str
    """吧名"""
    title: str
    """标题"""
    url: str
    """链接"""

    @property
    def log(self) -> str:
        log = f"吃瓜推送事件：[{self.title}]"
        return log
    
    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return {"type":"818", "server": self.server, "name": self.name, "msg":f"有新的八卦推送来啦！\n{self.title}\n{self.url}\n来源：{self.name}吧"}

@EventRister.rister(action=1001)
class SerendipityEvent(RecvEvent):
    """奇遇播报事件"""

    __event__ = "WsRecv.Serendipity"
    message_type = "Serendipity"
    name: str
    """触发角色"""
    serendipity: str
    """奇遇名"""
    level: int
    """奇遇等级"""
    time: str
    """触发时间"""

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%m/%d %H:%M")

    @property
    def log(self) -> str:
        log = f"奇遇推送事件：[{self.server}]的[{self.name}]抱走了奇遇：{self.serendipity}"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return Message(f"奇遇推送 {self.time}\n{self.serendipity} 被 {self.name} 抱走惹。")


@EventRister.rister(action=1002)
class HorseRefreshEvent(RecvEvent):
    """马驹刷新事件"""

    __event__ = "WsRecv.HorseRefresh"
    message_type = "HorseRefresh"
    map: str
    """刷新地图"""
    min: int
    """时间范围min"""
    max: int
    """时间范围max"""
    time: str
    """推送时间"""

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%H:%M:%S")

    @property
    def log(self) -> str:
        log = f"马驹刷新推送：[{self.server}]的[{self.map}]将要在 {str(self.min)}-{str(self.max)} 分后刷新马驹。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return Message(
            f"[抓马监控] 时间：{self.time}\n{self.map} 将在[{self.min} - {self.max}分]后刷新马驹。"
        )


@EventRister.rister(action=1003)
class HorseCatchedEvent(RecvEvent):
    """马驹捕获事件"""

    __event__ = "WsRecv.HorseCatched"
    message_type = "HorseCatched"
    name: str
    """触发角色名"""
    map: str
    """地图"""
    horse: str
    """马驹名"""
    time: str
    """事件时间"""

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%H:%M:%S")

    @property
    def log(self) -> str:
        log = f"马驹被抓事件：[{self.server}]的[{self.name}]在[{self.map}]捕获了 {self.horse} 。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return Message(
            f"[抓马监控] 时间：{self.time}\n{self.map} 的 {self.horse} 被 {self.name} 抓走了~"
        )


@EventRister.rister(action=1004)
class FuyaoRefreshEvent(RecvEvent):

    __event__ = "WsRecv.FuyaoRefresh"
    message_type = "FuyaoRefresh"
    time: str

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%H:%M:%S")

    @property
    def log(self) -> str:
        log = f"扶摇刷新事件：[{self.server}]的扶摇开始刷新 。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return Message(f"[扶摇监控]\n扶摇九天在 {self.time} 开启了。")


@EventRister.rister(action=1005)
class FuyaoNamedEvent(RecvEvent):
    """扶摇点名事件"""

    __event__ = "WsRecv.FuyaoNamed"
    message_type = "FuyaoNamed"
    names: list[str]
    """点名角色组"""
    time: str
    """点名时间"""

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%H:%M:%S")

    @property
    def log(self) -> str:
        name = ",".join(self.names)
        log = f"扶摇点名事件：[{self.server}]的扶摇点名了，玩家[{name}] 。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        name = ",".join(self.names)
        return Message(f"[扶摇监控] 时间：{self.time}\n唐文羽点名了[{name}]。")


@EventRister.rister(action=1006)
class FireworksEvent(RecvEvent):
    """烟花播报事件"""

    __event__ = "WsRecv.Fireworks"
    message_type = "Fireworks"
    role: str
    """烟花地图"""
    name: str
    """接受烟花的角色"""
    sender: str
    """使用烟花的角色"""
    recipient: str
    """烟花名字"""
    time: str
    """烟花使用时间"""

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%H:%M:%S")

    @property
    def log(self) -> str:
        log = f"烟花事件：{self.sender} 在 {self.map} 对 {self.name} 使用了烟花：{self.recipient}。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return Message(
            f"[烟花监控] 时间：{self.time}\n{self.sender} 在 {self.map} 对 {self.name} 使用了烟花：{self.recipient}。"
        )


@EventRister.rister(action=1007)
class XuanJingEvent(RecvEvent):
    """玄晶获取事件"""

    __event__ = "WsRecv.XuanJing"
    message_type = "XuanJing"
    role: str
    """角色名"""
    map: str
    """地图名"""
    name: str
    """玄晶名"""
    time: str
    """获取时间"""
    server: str

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def log(self) -> str:
        log = f"玄晶事件：【{self.server}】[{self.time}] 侠士 {self.role} 在 {self.map} 获取了 {self.name}。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        xuanjing_record_file = ASSETS + "/jx3/xuanjing.json"
        correct = json.loads(read(xuanjing_record_file))
        found = False
        for i in correct:
            if i["server"] == self.server:
                found = True
                new = {"time":self.time, "map":self.map, "role":self.role, "name":self.name}
                i["records"].append(new)
        if found == False:
            return
        write(xuanjing_record_file, json.dumps(correct, ensure_ascii=False))
        return {"type":"玄晶","server":f"{self.server}","msg":f"{self.time}\n【{self.server}】恭喜侠士[{self.role}]在{self.map}获得稀有掉落[{self.name}]！"}


@EventRister.rister(action=1008)
class GameSysMsgEvent(RecvEvent):
    """游戏系统频道消息推送"""

    __event__ = "WsRecv.GameSysMsg"
    message_type = "GameSysMsg"
    message: str
    """消息内容"""
    time: str
    """消息时间"""

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%H:%M:%S")

    @property
    def log(self) -> str:
        log = f"系统频道推送：{self.message}。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return Message(f"[系统频道推送]\n时间：{self.time}\n{self.message}。")


@EventRister.rister(action=10001)
class SubscribeEvent(RecvEvent):
    """订阅回执"""

    __event__ = "WsRecv.Subscribe"
    message_type = "Subscribe"
    action: Literal["烟花报时", "玄晶报时", "游戏消息"]
    """订阅内容"""
    server: list
    """已订阅服务器"""

    @validator("action", pre=True)
    def check_action(cls, v):
        if v == 1006:
            return "烟花报时"
        elif v == 1007:
            return "玄晶报时"
        elif v == 1010:
            return "游戏消息"

    @property
    def log(self) -> str:
        log = f"订阅回执，类型：{self.action}。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return Message(f"[订阅回执]\n类型：{self.action}。")

@EventRister.rister(action=10002)
class DisSubscribeEvent(RecvEvent):
    """取消订阅回执"""

    __event__ = "WsRecv.DisSubscribe"
    message_type = "DisSubscribe"
    action: Literal["烟花报时", "玄晶报时", "游戏消息"]
    """订阅内容"""
    server: list[str]
    """已订阅服务器"""

    @validator("action", pre=True)
    def check_action(cls, v):
        if v == 1006:
            return "烟花报时"
        elif v == 1007:
            return "玄晶报时"
        elif v == 1010:
            return "游戏消息"

    @property
    def log(self) -> str:
        log = f"取消订阅回执，类型：{self.action}。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return Message(f"[取消订阅回执]\n类型：{self.action}。")
