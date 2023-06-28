from ..dep import *


@EventRister.rister(action=2003)
class ClientUpdateRecEvent(RecvEvent):
    """更新推送事件"""

    __event__ = "WsRecv.ClientUpdate"
    message_type = "ClientUpdate"
    user_message_type: str = '更新'  # 用户定义的事件名称
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
    def render_message(self, group) -> str:
        return self.get_message()

    @overrides(RecvEvent)
    def get_message(self) -> str:
        return f"检测到客户端有更新哦~\n当前版本：{self.old_version}\n更新版本：{self.new_version}\n共计{self.package_num}个更新包，总大小为{self.package_size}。"
