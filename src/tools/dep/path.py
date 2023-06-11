from .bot import *
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
DATA = TOOLS[:-5] + "data"
CACHE = TOOLS[:-5] + "cache"
ASSETS = TOOLS[:-5] + "assets"
