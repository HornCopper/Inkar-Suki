from src.tools.config import Config
from src.tools.basic.msg import PROMPT
from src.tools.basic.data_server import server_mapping
from src.tools.utils.request import get_api

token = Config.jx3.api.token
bot_name = Config.bot_basic.bot_name_argument

async def demon_(server: str = None, group_id: str = None):  # 金价 <服务器>
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT.ServerNotExist]
    final_url = f"{Config.jx3.api.url}/view/trade/demon?robot={bot_name}&server={server}&chrome=1&token={token}"
    data = await get_api(final_url)
    if data["code"] == 400:
        return ["服务器名输入错误，请检查后重试~"]
    return data["data"]["url"]
