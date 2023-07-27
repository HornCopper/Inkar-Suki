from typing import List
from src.tools.utils import get_api
import sys
import nonebot
import re

TOOLS = nonebot.get_driver().config.tools_path
ASSETS = TOOLS[:-5] + "assets"
PLUGINS = TOOLS[:-5] + "plugins"

class PetInfo:
    basic = "https://www.jx3box.com/pet/"
    def __init__(self, pet: dict) -> None:
        self.name = pet["Name"]
        self.clue = pet["OutputDes"].split("=")[1][1:].split("font")[0].replace("\" ", "")
        desc_ = pet["Desc"].split("=")[1][1:].split("font")[0].replace("\" ", "")
        self.desc = re.sub(r"\\.*", "", desc_)
        p = pet["Index"]
        self.url = f"{PetInfo.basic}{p}"

async def get_pet(pet: str) -> List[PetInfo]:
    # 数据来源@JX3BOX
    final_url = f"https://node.jx3box.com/pets?per=12&page=1&Class=&Name={pet}&Source=&client=std"
    data = await get_api(final_url)
    data = [PetInfo(x) for x in data["list"]]
    return data
