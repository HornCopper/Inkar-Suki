from src.tools.basic import *


async def sandbox_(server: str):
    """沙盘 <服务器>"""
    if not server:
        return [PROMPT_ServerNotExist]
    if server is not None:
        final_url = f"{Config.jx3.api.url}/view/server/sand?token={token}&chrome=1&nickname={bot}&server={server}"
    data = await get_api(final_url)
    if data["code"] == 400:
        return [PROMPT_ServerInvalid]
    return data["data"]["url"]

async def sandbox_v2_(server: str):
    """沙盘v2 <服务器>"""
    if not server:
        return [PROMPT_ServerNotExist]
    if server is not None:
        final_url = f"{Config.jx3.api.url}/data/server/sand?token={token}&server={server}"
    data = await get_api(final_url)
    if data["code"] == 400:
        return [PROMPT_ServerInvalid]
    html = read(VIEWS + "/jx3/pvp/sandbox.html")
    update_time = convert_time(data["data"]["update"])
    html = html.replace("$time", update_time)
    html = html.replace("$server", server)
    for i in data["data"]["data"]:
        camp = "haoqi" if i["campName"] == "浩气盟" else "eren"
        html = html.replace("$" + i["castleName"], camp)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".m-sandbox-map", False)
    return Path(final_path).as_uri()