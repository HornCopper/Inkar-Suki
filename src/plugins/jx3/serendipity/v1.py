from src.tools.basic import *

async def serendipity_(server: str = None, name: str = None, group_id: str = None):  # 奇遇 <服务器> <ID>
    if token is None:
        return [PROMPT_NoToken]
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    final_url = f"{Config.jx3.api.url}/view/luck/adventure?token={token}&nickname={bot}&ticket={ticket}&server={server}&name={name}&chrome=1"
    data = await get_api(final_url)
    return data["data"]["url"]


# 近期奇遇 <服务器> [奇遇]
async def statistical_(server: str = None, serendipity: str = None, group_id: str = None):
    if token is None:
        return [PROMPT_NoToken]
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    if serendipity is None:
        final_url = f"{Config.jx3.api.url}/view/luck/collect?token={token}&nickname={bot}&server={server}&chrome=1"
    else:
        final_url = f"{Config.jx3.api.url}/view/luck/statistical?token={token}&nickname={bot}&ticket={ticket}&server={server}&name={serendipity}&chrome=1"
    data = await get_api(final_url)
    return data["data"]["url"]


async def global_serendipity(name: str = None):  # 全服奇遇 [奇遇]
    if token is None:
        return [PROMPT_NoToken]
    if name is not None:
        final_url = f"{Config.jx3.api.url}/view/luck/server/adventure?name={name}&token={token}&nickname={bot}&chrome=1"
    data = await get_api(final_url)
    return data["data"]["url"]


async def global_statistical(name: str = None):  # 全服统计 [奇遇]
    if token is None:
        return [PROMPT_NoToken]
    if name is not None:
        final_url = f"{Config.jx3.api.url}/view/luck/server/statistical?name={name}&token={token}&nickname={bot}"
    data = await get_api(final_url)
    return data["data"]["url"]

async def get_preposition(name: str = None):
    url = "https://inkar-suki.codethink.cn/serendipity"
    data = await get_api(url)
    flag = False
    for i in data:
        if i["name"] == name:
            id = i["id"]
            flag = True
    if not flag:
        return False
    final_url = "https://jx3box.com/adventure/" + str(id)
    return f"【{name}】魔盒攻略：\n{final_url}"