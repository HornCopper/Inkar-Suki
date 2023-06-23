from src.tools.dep import *

async def zone(server, id):
    server = server_mapping(server)
    final_url = f"https://www.jx3api.com/view/role/teamCdList?token={token}&server={server}&name={id}&ticket={ticket}&robot={bot}&scale=1"
    data = await get_api(final_url)
    if data["code"] == 404:
        return ["玩家不存在或尚未在世界频道发言哦~"]
    return data["data"]["url"]

async def get_cd(server: str, sep: str):
    url = f"https://pull.j3cx.com/api/serendipity?server={server}&serendipity={sep}&pageSize=1"
    data = await get_api(url)
    data = data.get("data").get('data')
    if not data:
        return "没有记录哦~"
    data = data[0]
    time = data["date_str"]
    msg = f"「{server}」服务器上一次记录「{sep}」：\n{time}\n数据来源：@茗伊插件集"
    return msg