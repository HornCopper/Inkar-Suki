import sys
import nonebot
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
from utils import get_api

async def mcjavav():
    info = await get_api("https://api.codethink.top/mcv?platform=j")
    rl = info["release"]
    ss = info["snapshot"]
    return f"找到Java版本信息啦~\n最新快照：{ss}\n最新正式版：{rl}"
async def mcbedrockv():
    info = await get_api("https://api.codethink.top/mcv?platform=b")
    rl = info["release"]
    bt = info["beta"]
    return f"找到基岩版版本信息啦~\n最新测试版：{bt}\n最新正式版：{rl}"
