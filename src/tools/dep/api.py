from src.tools.utils import *
from sgtpyutils import extensions
from src.tools.config import Config
from src.plugins.jx3.jx3apiws import ws_client, Jx3WebSocket, RecvEvent
from src.constant.jx3 import *
token = Config.jx3api_globaltoken
bot = "Inkar-Suki"
ticket = Config.jx3_token
proxies = None
