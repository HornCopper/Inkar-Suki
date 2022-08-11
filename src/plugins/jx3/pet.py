import sys
import nonebot
from pathlib import Path
from nonebot.adapters.onebot.v11 import MessageSegment
from bs4 import BeautifulSoup
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
ASSETS = TOOLS[:-5] + "assets"
PLUGINS = TOOLS[:-5] + "plugins"
from utils import get_api, get_content, get_status, checknumber

'''
状态码：
    201 - 搜索 包含 status result clue desc
    404 - 没找到任何结果
'''

async def get_pet(pet: str):
    final_url = f"https://node.jx3box.com/pets?per=12&page=1&Class=&Name={pet}&Source=&client=std"
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
        desc.append(data["Desc"].split("=")[1][1:].split("font")[0].replace("\" ",""))
        url.append(basic + str(data["Index"]))
        return {"status":201, "result": result, "clue": clue, "desc": desc, "url": url}
    elif count >= 6:
        return {"status":404} # 暂时摆烂
    elif count == 0:
        return {"status":404} # 不是摆烂
    else:
        raise ValueError("Unexcept Error! Please check the api instead of the source code.")