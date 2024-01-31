import random
from src.tools.dep.data_server import *
from src.tools.utils import *
from src.tools.config import Config
_bot = Config.bot
_token = Config.jx3api_globaltoken
_saohua_db = filebase_database.Database(f"{bot_path.common_data_full}pvx-saohua").value
if not _saohua_db.get("items"):
    _saohua_db["items"] = ["好，这里显示一条骚话"]


async def saohua(cache_rate: float = 0.95):
    items = _saohua_db["items"]
    if random.random() < cache_rate:
        return random.choice(items)
    buff = await get_api(f"https://www.jx3api.com/data/saohua/random?token={_token}")
    data = buff.get("data") or {}
    _saohua = data.get("text")
    if _saohua:
        items.append(_saohua)
        return _saohua
    return random.choice(_saohua_db)
