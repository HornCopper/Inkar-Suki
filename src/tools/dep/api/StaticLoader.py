from __future__ import annotations
from typing import Literal
import threading
import json
from src.tools.utils import *
from src.tools.file import *


class StaticLoader:
    lock = threading.Lock()

    inited: bool = False
    key: str  # from_id使用此字段

    static_data: dict[str, StaticLoader] = None
    resource_url: str
    resource_type: Literal['http', 'file'] = 'http'

    @classmethod
    def init(cls):
        with cls.lock:
            if cls.inited:
                return
            if cls.resource_type == 'http':
                t = get_api(cls.resource_url)
                __raw_data: dict[str, dict[str, dict]] = ext.SyncRunner.as_sync_method(t)
            else:
                __raw_data = json.loads(read(cls.resource_url))
            raw_data: dict[str, cls] = {}
            if not __raw_data:
                return logger.error(f'fail to load resources:{cls.__name__}')
            for x in __raw_data:
                item = cls(x, __raw_data[x])
                if not hasattr(item, 'key'):
                    item.key = x  # 未设置则主动设置
                raw_data[item.key] = item

            cls.inited = True
            cls.static_data = raw_data

    @classmethod
    def from_id(cls, key: str):
        if not cls.inited:
            cls.init()
        result = cls.static_data.get(str(key))
        if not result:
            logger.warning(f'not found resources:{cls.__name__}@{key}')
        return result
