from ..lib import *


async def render_items(server: str, items: List[GoodsInfo]):
    '''
    渲染带价格概况的物品列表
    '''
    data = dict([[x.id, x.to_dict()] for x in items])
    data = json.dumps(data, cls=GoodsSerializerEncoder)
    data = json.loads(data)
    img = await get_render_image('src/views/jx3/trade/goods_list.html', {
        'items': data,
        'server': server
    }, delay=1000)
    return img
