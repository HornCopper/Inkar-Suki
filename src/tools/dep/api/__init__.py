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
ticket = Config.jx3_token
proxies = None
