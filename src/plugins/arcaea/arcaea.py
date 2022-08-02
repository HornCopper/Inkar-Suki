import json, sys, nonebot
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
from utils import get_url

async def getUserInfo(nickname: str) -> str:
    