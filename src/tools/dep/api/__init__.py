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
token = Config.jx3api_globaltoken
bot = "Inkar-Suki"
proxies = None

# initilize jx3-ticket
ticket = Config.jx3_token
device_id = ticket and ticket.split("::")
device_id = device_id[1] if device_id and len(device_id) > 1 else None

# initilize private api
try:
    from src.tools.dep.jx3.tuilan import gen_ts, gen_xsk, format_body, dungeon_sign  # 收到热心网友举报，我们已对推栏的算法进行了隐藏。
except:
    pass
