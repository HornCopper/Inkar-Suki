from .config import Config
token = Config.jx3.api.token
bot = "Inkar-Suki"

ticket = Config.jx3.api.ticket
device_id = ticket and ticket.split("::")
device_id = device_id[1] if device_id and len(device_id) > 1 else None