from src.tools.dep.api import *
from src.tools.dep.server import *

async def addritube_(server: str = None, name: str = None): # 查装 <服务器> <ID>
    if token == None or ticket == None:
        return ["Bot尚未填写Ticket或Token，请联系Bot主人~"]
    server = server_mapping(server)
    if server == False:
        return [PROMPT_ServerInvalid]
    final_url = f"https://www.jx3api.com/view/role/attribute?ticket={ticket}&token={token}&robot={bot}&server={server}&name={name}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 404:
        return ["唔……玩家不存在。"]
    if data["code"] == 403 and data["msg"] == "侠客隐藏了游戏信息":
        return ["唔，该玩家隐藏了信息。"]
    if data["code"] == 403 and data["msg"] == "仅互关好友可见":
        return ["仅互关好友可见哦~"]
    return data["data"]["url"]


async def roleInfo_(server, player):
    server = server_mapping(server)
    final_url = f"https://www.jx3api.com/data/role/roleInfo?token={token}&name={player}&server={server}"
    if server == False:
        return PROMPT_ServerInvalid
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 404:
        return "没有找到该玩家哦~\n需要该玩家在世界频道发言后方可查询。"
    msg = "以下信息仅供参考！\n数据可能已经过期，但UID之类的仍可参考。"
    zone = data["data"]["zoneName"]
    srv = data["data"]["serverName"]
    nm = data["data"]["roleName"]
    uid = data["data"]["roleId"]
    fc = data["data"]["forceName"]
    bd = data["data"]["bodyName"]
    tg = data["data"]["tongName"]
    cp = data["data"]["campName"]
    msg = msg + f"\n服务器：{zone} - {srv}\n角色名称：{nm}\nUID：{uid}\n体型：{fc}·{bd}\n帮会：{cp} - {tg}"
    return msg
    

