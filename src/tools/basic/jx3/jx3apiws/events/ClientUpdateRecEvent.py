from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=2003)
class ClientUpdateRecEvent(RecvEvent):
    """更新推送事件"""

    __event__: str = "WsRecv.ClientUpdate"
    message_type: str = "ClientUpdate"
    now_version: str
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
        return {"type": "更新", "msg": f"检测到客户端有更新哦~\n当前版本：{self.now_version}\n更新版本：{self.new_version}\n共计{self.package_num}个更新包，总大小为{self.package_size}。"}
