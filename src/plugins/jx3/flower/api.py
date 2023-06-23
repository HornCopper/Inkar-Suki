from src.tools.dep import *


async def get_flower(server: str):
    url = f'https://www.jx3api.com/data/home/flower?scale=2&server={server}&robot={bot}'
    data = await get_api(url)
    if not data['code'] == 200:
        return f'获取花价失败了,{data["msg"]}'
    return data['data']
