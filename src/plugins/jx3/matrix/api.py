from src.constant.jx3 import aliases

from src.tools.config import Config
from src.tools.utils.request import get_api

token = Config.jx3.api.token

async def matrix_(name):
    name = aliases(name)
    if name is False:
        return "此心法不存在哦~请检查后重试。"
    full_link = f"{Config.jx3.api.url}/data/school/matrix?name={name}&token={token}"
    info = await get_api(full_link)
    if info["code"] == 400:
        return "此心法不存在哦~请检查后重试。"
    else:
        description = ""

        def fe(f, e):
            return f"{f}：{e}\n"
        for i in info["data"]["descs"]:
            description = description + fe(i["name"], i["desc"])
        skillName = info["data"]["skillName"]
        return f"查到了{name}的{skillName}：\n" + description
