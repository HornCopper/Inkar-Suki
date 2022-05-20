import sys, nonebot, json
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
from http_ import http

async def mcjavav():
    info = json.loads(await http.get_url("https://api.codethink.top/mcv?platform=j"))
    rl = info["release"]
    ss = info["snapshot"]
    return f"找到Java版本信息啦~\n最新快照：{ss}\n最新正式版：{rl}"
async def mcbedrockv():
    info = json.loads(await http.get_url("https://api.codethink.top/mcv?platform=b"))
    rl = info["release"]
    bt = info["beta"]
    return f"找到基岩版版本信息啦~\n最新测试版：{bt}\n最新正式版：{rl}"
