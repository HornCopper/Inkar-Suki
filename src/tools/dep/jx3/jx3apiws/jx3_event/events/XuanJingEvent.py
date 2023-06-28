from ..dep import *
from sgtpyutils.logger import logger


@EventRister.rister(action=1007)
class XuanJingEvent(RecvEvent):
    """玄晶获取事件"""

    __event__ = "WsRecv.XuanJing"
    message_type = "XuanJing"
    user_message_type: str = '玄晶'  # 用户定义的事件名称
    role: str
    """角色名"""
    map: str
    """地图名"""
    name: str
    """玄晶名"""
    time: str
    """获取时间"""

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def log(self) -> str:
        log = f"玄晶事件：【{self.server}】[{self.time}] 侠士 {self.role} 在 {self.map} 获取了 {self.name}。"
        return log

    @overrides(RecvEvent)
    def render_message(self, group) -> str:
        return self.get_message()

    @property
    def record(self) -> dict:
        return {"time": self.time, "map": self.map,
                "role": self.role, "name": self.name}

    def check_database(self) -> bool:
        xuanjing_record_file = f"{ASSETS}{os.sep}jx3{os.sep}xuanjing.json"
        correct = json.loads(read(xuanjing_record_file))
        for i in correct:
            if not i.get("server") == self.server:
                continue
            new = self.record
            i["records"].append(new)
            write(xuanjing_record_file, json.dumps(
                correct, ensure_ascii=False))
            return True
        return False

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        if not self.check_database():
            logger.warning(
                f'xuanjing update:invalid server[{self.server}]{self.record}')
            return None
        return f"{self.time}\n【{self.server}】恭喜侠士[{self.role}]在{self.map}获得稀有掉落[{self.name}]！"
