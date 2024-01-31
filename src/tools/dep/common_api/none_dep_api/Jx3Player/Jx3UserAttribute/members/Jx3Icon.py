from src.tools.utils import *


class Jx3Icon:
    cache = filebase_database.Database(f"{bot_path.common_data_full}glo-icon")
    lock = threading.Lock()

    def __init__(self, filename: str) -> None:
        if isinstance(filename, dict):
            """{FileName:https://...,Kind:技能,SubKind:长歌}"""
            icon = filename.get("icon") or filename
            filename = icon.get("FileName") if isinstance(icon, dict) else icon
        self.filename: str = filename

    @property
    def img(self):
        with self.lock:
            filename = self.filename
            if filename is None:
                return None

            prev = self.cache.get(filename)
            if prev:
                return base64.b64decode(prev)
            # TODO 加载
            data = ext.SyncRunner.as_sync_method(get_content(filename))
            encoded = base64.b64encode(data).decode()
            self.cache[filename] = encoded
            return encoded
