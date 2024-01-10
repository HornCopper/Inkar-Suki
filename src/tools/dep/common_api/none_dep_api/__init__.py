from src.tools.dep.data_server import *
from src.tools.utils import *
from src.tools.dep.api.prompt import *
from src.tools.config import Config
_bot = Config.bot
_token = Config.jx3api_globaltoken

async def daily_(server: str = None, group_id: str = None, predict_day_num: int = 0):
    """
    获取日常图片链接
    @param predict_day_num 向后预测天数
    """
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    full_link = f"{Config.jx3api_link}/view/active/current?robot={_bot}&server={server}&num={predict_day_num}&token={_token}"
    data = await get_api(full_link)
    return data["data"]["url"]