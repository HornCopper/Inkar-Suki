from .Caches import *
import copy


def check_cache_integrity(current_cache: dict, new_data: dict):
    # 当前缓存没有缓存品数，应为其缓存
    cached_level = not current_cache.get('level') is None
    should_update_cache = not cached_level
    if not should_update_cache:
        return
    current_cache['level'] = new_data.get('Level')
    CACHE_Goods[current_cache['id']] = dict2obj(GoodsInfo(), current_cache)
    flush_CACHE_Goods()


async def from_id(id: str) -> GoodsInfoFull:
    '''
    通过id初始化
    '''
    data = await get_item_info_by_id(id)
    cache_data: GoodsInfo = CACHE_Goods.get(id)
    if not cache_data is None:
        current_cache = cache_data.to_dict()
        check_cache_integrity(current_cache, data)

        x = copy.deepcopy(current_cache)
        x.update(data)
        data = x

    return GoodsInfoFull(data)
GoodsInfoFull.from_id = from_id
