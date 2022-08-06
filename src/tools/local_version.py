import nonebot
import sys
import json
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
from utils import get_api

async def ikv():
    all_rls = await get_api("https://api.github.com/repos/codethink-cn/Inkar-Suki/releases")
    lst_rls = all_rls[0]["name"]
    all_cmt = await get_api("https://api.github.com/repos/codethink-cn/Inkar-Suki/commits")
    lst_cmt = all_cmt[0]["sha"][0:7]
    return f"{lst_rls}({lst_cmt})"

nbv = nonebot.__version__