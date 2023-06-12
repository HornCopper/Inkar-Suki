from src.tools.dep.api import *
from src.tools.dep.server import *

async def pendant(name: str):
    final_url = f"https://www.jx3api.com/data/other/pendant?name={name}&token={token}"
    data = await get_api(final_url)
    if data["code"] == 404:
        return "没有找到该挂件哦~"
    else:
        data = data["data"][0]
        pendant_type = data["class"]
        pendant_name = data["name"]
        desc = data["desc"]
        source = data["source"]
        msg = f"{pendant_name} - {pendant_type}\n{desc}\n获取线索：{source}"
        return msg

