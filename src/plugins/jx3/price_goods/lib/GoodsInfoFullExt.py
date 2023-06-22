from .Caches import *
import copy

async def from_id(id: str) -> GoodsInfoFull:
    '''
    通过id初始化
    '''
    data = await get_item_info_by_id(id)
    cache_data: GoodsInfo = CACHE_Goods.get(id)
    if not cache_data is None:
        x = copy.deepcopy(cache_data.to_dict())
        x.update(data)
        data = x
    return GoodsInfoFull(data)

GoodsInfoFull.from_id = from_id
