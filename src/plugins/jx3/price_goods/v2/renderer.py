from ..lib import *


async def render_items(server: str, arg_item: str, arg_page: int, pageSize: int, totalCount: int, items: List[GoodsInfo], template: str = 'goods_list'):
    '''
    渲染带价格概况的物品列表
    '''
    data = dict([[x.id, x.to_dict()] for x in items])
    data = json.dumps(data, cls=GoodsSerializerEncoder)
    data = json.loads(data)
    img = await get_render_image(f'src/views/jx3/trade/{template}.html', {
        'items': data,
        'server': server,
        'item_name': arg_item,
        'page': {
            'pageIndex': arg_page,
            'pageSize': pageSize,
            'totalCount': totalCount
        }

    }, delay=200)
    return img


async def render_detail_item(server: str, arg_item: GoodsInfo, arg_price: GoodsPriceDetail, price_logs: List):
    '''
    渲染单个物品价格详情
    '''
    data = {
        'server': server,
        'item': arg_item.to_dict(),
        'price_detail': arg_price.to_dict(),
        'price_logs': price_logs
    }
    data = json.dumps(data, cls=GoodsSerializerEncoder)
    data = json.loads(data)
    img = await get_render_image('src/views/jx3/trade/price_detail.html', data, delay=200)
    return img
