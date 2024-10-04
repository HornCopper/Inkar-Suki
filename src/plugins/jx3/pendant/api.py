from src.config import Config
from src.utils.network import Request
from src.utils.decorators import token_required

@token_required
async def pendant(name: str, token: str):
    final_url = f"{Config.jx3.api.url}/data/other/pendant?name={name}&token={token}"
    data = (await Request(final_url).get()).json()
    if data["code"] != 200:
        return "没有找到该挂件哦~"
    else:
        data = data["data"][0]
        pendant_type = data["class"]
        pendant_name = data["name"]
        desc = data["desc"]
        source = data["source"]
        msg = f"{pendant_name} - {pendant_type}\n{desc}\n获取线索：{source}"
        return msg