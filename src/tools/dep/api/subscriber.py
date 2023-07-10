from src.tools.utils import *
from ..data_server import *


def load_or_write_subscribe(group_id: str, data: dict = None) -> dict[str, dict]:
    '''
    加载或写入群的订阅信息
    @return {subject:data}
    '''
    path = f"{DATA}/{group_id}/subscribe.json"
    if not data is None:
        write(path, json.dumps(data, ensure_ascii=False))
        return data
    now = json.loads(read(path))
    if not isinstance(now, dict):
        # 用于记录更多信息
        now = dict([[x, {}] for x in now])
    return now
