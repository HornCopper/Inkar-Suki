from .config import Config
token = Config.jx3api_globaltoken
bot = "Inkar-Suki"
proxies = None

ticket = Config.jx3_token
device_id = ticket and ticket.split("::")
device_id = device_id[1] if device_id and len(device_id) > 1 else None