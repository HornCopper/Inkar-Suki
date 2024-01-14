
from src.tools.dep import *


@Jx3Arg.requireTicket
@Jx3Arg.requireToken
async def addritube_(server: str = None, name: str = None):
    '''# 查装 <服务器> <ID>'''
    final_url = f"{Config.jx3api_link}/view/role/attribute?ticket={ticket}&token={token}&robot={bot}&server={server}&name={name}&scale=1"
    data = await get_api(final_url)
    return Jx3ApiResponse(data).output_url
