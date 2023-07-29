'''
网络请求相关组件
'''
from .subscriber import *
from sgtpyutils.logger import logger
import time
from .img_renderer import *
from .argparser import *
import json
from src.tools.config import Config
token: str = Config.jx3api_globaltoken
bot: str = "Inkar-Suki"
ticket: str = Config.jx3_token
device_id: str = ticket.split("::")[1] if ticket else None
proxies: dict[str, str] = None  # {"https":"https://127.0.0.1:8080"}
