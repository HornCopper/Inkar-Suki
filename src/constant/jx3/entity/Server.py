from .Base import *
from src.tools.utils import *

server_status_records: dict[str, dict[str, str]] = filebase_database.Database(
    f"{common_data_full}server_status_records",
).value


class ServerRecordType(enum.Enum):
    unknown = 0
    last_stop = 1  # 上次维护
    last_start = 2  # 上次开服


class Server(Aliasable):
    """服务器"""
    database = "./config.server"

    @property
    def record(self):
        if result := server_status_records.get(self.name):
            return result
        result = {}
        for rec in [x for x in ServerRecordType if x.value > 0]:
            result[rec.name] = None

        server_status_records[self.name] = result
        return result

    @record.setter
    def record(self, val: dict[str, str]):
        server_status_records[self.name] = val

    def get_record(self, record_type: ServerRecordType, val: any = Ellipsis) -> any:
        record = self.record
        if isinstance(record_type, ServerRecordType):
            record_type = record_type.name
        prev = record.get(record_type)
        if val is not Ellipsis:
            record[record_type] = val
        return prev

    @property
    def record_desc(self) -> str:
        start: int = self.get_record(ServerRecordType.last_start)
        stop: int = self.get_record(ServerRecordType.last_stop)
        none = "暂无"
        msg = f"上次开服:{start or none}\n上次维护:{stop or none}"
        if start and stop:
            delta = (DateTime(stop) - DateTime(start)).total_seconds()
            if delta > 0:
                msg = f"{msg}\n维护耗时:{int(delta/60)}分钟"

        return msg
