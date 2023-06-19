from ..lib import *


async def render_items(server: str, arg_item: str, arg_page: int, pageSize: int, totalCount: int, items: List[GoodsInfo]):
    '''
    渲染带价格概况的物品列表
    '''
    data = dict([[x.id, x.to_dict()] for x in items])
    data = json.dumps(data, cls=GoodsSerializerEncoder)
    data = json.loads(data)
    img = await get_render_image('src/views/jx3/trade/goods_list.html', {
        'items': data,
        'server': server,
        'item_name': arg_item,
        'page': {
            'pageIndex': arg_page,
            'pageSize': pageSize,
            'totalCount': totalCount
        }

    }, delay=1000)
    return img
