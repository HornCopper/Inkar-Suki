# TODO 支持aop.require方式获取参数
# 参数不存在时则返回错误

# def require_config():
# class configs(enum)

from src.tools.config import Config
from src.tools.config import Config as gloConfig
token = Config.jx3api_globaltoken
bot = "Inkar-Suki"
proxies = None

# initilize jx3-ticket
ticket = Config.jx3_token
device_id = ticket and ticket.split("::")
device_id = device_id[1] if device_id and len(device_id) > 1 else None