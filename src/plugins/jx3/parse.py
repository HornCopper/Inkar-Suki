from __future__ import annotations
from pydantic import BaseModel
from typing import Literal, Callable, Type, Dict, Tuple
from dataclasses import dataclass

from src.tools.utils.time import get_current_time, convert_time

handler: Dict[int, Callable[[dict], JX3APIPushEvent]] = {}

def handle_event(action: int):
    def decorator_func(event_class: Type[JX3APIPushEvent]):
        handler[action] = event_class # type: ignore
        return event_class
    return decorator_func

@dataclass
class JX3APIOutputMsg:
    name: str = ""
    msg: str = ""
    server: str = ""

class JX3APIPushEvent(BaseModel):
    action: int = 0
    data: dict = {}

@handle_event(2001)
class JX3APIServerEvent(JX3APIPushEvent):
    server: str = ""
    status: Literal[0, 1] = 0

    def msg(self) -> JX3APIOutputMsg:
        status_str = "开服" if self.status else "维护"
        current_time = convert_time(get_current_time(), "%H:%M")
        return JX3APIOutputMsg(msg=f"{self.server} {status_str}啦！ 在{current_time}", server=self.server, name="开服")

@handle_event(2002)
class JX3APINewsEvent(JX3APIPushEvent):
    title: str = ""
    url: str = ""
    date: str = ""

    def msg(self) -> JX3APIOutputMsg:
        return JX3APIOutputMsg(msg=f"有新的官方公告！\n标题：{self.title}\n链接：{self.url}\n日期：{self.date}", name="公告")
    
    def provide_data(self) -> Tuple[str, str]:
        return self.url, self.title

@handle_event(2003)
class JX3APIClientUpdateEvent(JX3APIPushEvent):
    now_version: str = ""
    new_version: str = ""
    package_num: int = 0
    package_size: str = ""

    def msg(self) -> JX3APIOutputMsg:
        return JX3APIOutputMsg(msg=f"检测到游戏客户端更新！\n版本：{self.now_version} -> {self.new_version}\n本次更新有{self.package_num}个更新包，共计{self.package_size}！", name="更新")

@handle_event(2004)
class JX3API818Event(JX3APIPushEvent):
    name: str = ""
    title: str = ""
    url: str = ""
    server: str = ""

    def msg(self) -> JX3APIOutputMsg:
        return JX3APIOutputMsg(msg=f"有新的八卦推送来啦！\n标题：{self.title}\n{self.url}\n来源：{self.name}吧", name="818")

@handle_event(2005)
class JX3APIPassEvent(JX3APIPushEvent):
    server: str = ""
    castle: str = ""
    start: int = 0

    def msg(self) -> JX3APIOutputMsg:
        return JX3APIOutputMsg(msg=f"{self.server} 的【{self.castle}】变为 可争夺 状态！", server=self.server, name="关隘")
    

@handle_event(2006)
class JX3APIYuncongEvent(JX3APIPushEvent):
    name: str = ""
    site: str = ""
    desc: str = ""

    def msg(self) -> JX3APIOutputMsg:
        return JX3APIOutputMsg(msg=f"云从社的 {self.name}（{self.desc}）活动即将在10分钟后开始，敬请留意！", name="云从")

def parse_data(raw_data: dict):
    data = JX3APIPushEvent(**raw_data)
    action: int = data.action
    body: dict = data.data
    handler_class = handler.get(action)
    return handler_class(**body)  # type: ignore

def get_registered_actions():
    return list(handler.keys())