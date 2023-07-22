from src.tools.dep import *


async def get_flower(server: str, map: str = None, species: str = None):
    return await get_flower_by_tuilan(server, map, species)


async def get_flower_by_jx3api(server: str, map: str = None, species: str = None):
    url = f'{Config.jx3api_link}/data/home/flower?scale=2&server={server}&robot={bot}'
    data = await get_api(url)
    if not data.get('code') == 200:
        return f'获取花价失败了,{data["msg"]}'
    return data.get('data')

async def get_flower_by_tuilan(server: str, map: str = None, species: str = None):
    url = f'https://w.pvp.xoyo.com:31727/api/h5/jx3/flower/get-flowers-info'
    data = {"server": server, "map": map, "species": species}
    result = await post_url(url, json=data)
    result = json.loads(result)
    if not result.get("code") == 0:
        return f'获取花价失败了,{result.get("msg")}'
    result = result.get("data")
    logger.debug(f'flower-result[server{server}:map{map}:species{species}]\n{len(data)}')
    return convert_data(result)

def convert_data(raw: dict):
    '''
    将tuilan数据转换为标准数据
    '''
    result = {}
    if not raw:
        return result
    for x in raw:
        x_map = x.get('map')
        x_name = x.get('name').split('(')
        x_color = None
        if len(x_name) > 1: # 无色花则直接返回
            x_color = x_name[1][:-1]  # .split('，')
            x_name = x_name[0]
        x_species = x.get('species')
        x_line = [line.get('number') for line in x.get('branch')]
        x_price = 1.5
        item = {
            'color': x_color,
            'price': x_price,
            'name': x_name,
            'line': x_line,
            'species': x_species
        }
        if not result.get(x_map):
            result[x_map] = []
        result[x_map].append(item)
    return result