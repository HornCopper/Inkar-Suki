import sys
import nonebot
import re

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
ASSETS = TOOLS[:-5] + "assets"
PLUGINS = TOOLS[:-5] + "plugins"

from utils import get_api
from .jx3 import server_mapping

'''
状态码：
    201 - 搜索 包含 status result clue desc
    404 - 没找到任何结果
'''

async def get_pet(pet: str):
    final_url = f"https://node.jx3box.com/pets?per=12&page=1&Class=&Name={pet}&Source=&client=std" # 数据来源@JX3BOX
    data = await get_api(final_url)
    data = data["list"]
    count = len(data)
    basic = "https://www.jx3box.com/pet/"
    if count in [2,3,4,5]:
        return {"status":404} # 暂时摆烂
    elif count == 1:
        data = data[0]
        result = []
        clue = []
        desc = []
        url = []
        clue.append(data["OutputDes"].split("=")[1][1:].split("font")[0].replace("\" ",""))
        result.append(data["Name"])
        desc_ = data["Desc"].split("=")[1][1:].split("font")[0].replace("\" ","")
        info = re.sub(r"\\.*" , "", desc_)
        desc.append(info)
        url.append(basic + str(data["Index"]))
        return {"status":201, "result": result, "clue": clue, "desc": desc, "url": url}
    elif count >= 6:
        return {"status":404} # 暂时摆烂
    elif count == 0:
        return {"status":404} # 不是摆烂
    else:
        raise ValueError("Unexcept Error! Please check the api instead of the source code.")

async def get_cd(server: str, sep: str, group: str):
    server = server_mapping(server, group)
    url = f"https://pull.j3cx.com/api/serendipity?server={server}&serendipity={sep}&pageSize=1" # Thanks to @茗伊
    data = await get_api(url)
    data = data["data"]["data"][0]
    time = data["date_str"]
    msg = f"「{server}」服务器上一次记录「{sep}」：\n{time}\n数据来源：@茗伊插件集"
    return msg