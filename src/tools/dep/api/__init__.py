'''
网络请求相关组件
'''
import json
from sgtpyutils.logger import logger
from src.tools.config import Config
logger.debug('start load web renderer')
from .argparser import *
from .renderer import *
token = Config.jx3api_globaltoken
bot = "Inkar-Suki"
ticket = Config.jx3_token
proxies = None
