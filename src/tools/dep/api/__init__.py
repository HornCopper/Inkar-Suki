'''
网络请求相关组件
'''
from .subscriber import *
from .renderer import *
from .argparser import *
import json
from sgtpyutils.logger import logger
from src.tools.config import Config
logger.debug('start load web renderer')
token = Config.jx3api_globaltoken
bot = "Inkar-Suki"
ticket = Config.jx3_token
proxies = None
