from src.tools.dep import *

async def matrix_(name):
    name = aliases(name)
    if name == False:
        return "此心法不存在哦~请检查后重试。"
    full_link = "{Config.jx3api_link}/data/school/matrix?name=" + name
    info = await get_api(full_link, proxy = proxies)
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