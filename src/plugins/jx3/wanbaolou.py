import nonebot
import time
import sys

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from utils import get_api

async def get_wanbaolou(product_number: int, product_type: bool):
    def strange_time_number_to_person_s_message(strange_time_number: int):
        return f"{int(strange_time_number / 3600)}时{int((strange_time_number - int(strange_time_number / 3600) * 3600) /60)}分"
    
    def price_to_text(price: int):
        return f"￥{price / 100}"
    '''
    万宝楼外观/角色查询，使用18位商品编号。

    :product_type:

    `True`为外观；`False`为角色。
    '''
    if product_type:
        _good_type = 3
    else:
        _good_type = 2
    final_url = f"https://api-wanbaolou.xoyo.com/api/buyer/goods/list?goods_type={_good_type}&consignment_id={product_number}"
    data = await get_api(final_url)
    detail_data = data["data"]["list"][0]
    zone = detail_data["zone_name"]
    server = detail_data["server_name"]
    seller = detail_data["seller_role_name"]
    seller_full_info = f"{zone}-{server}-{seller}"
    product = detail_data["info"]
    remain = strange_time_number_to_person_s_message(detail_data["remaining_time"])
    price = price_to_text(detail_data["single_unit_price"])
    follower_count = detail_data["followed_num"]
    if product_type:
        product_detail_type = detail_data["attrs"]["appearance_type_name"]
        msg = f"商品名称：{product}\n售卖者：{seller_full_info}\n点赞：{follower_count}\n剩余时间：{remain}\n商品类型：{product_detail_type}\n价格：{price}"
        return msg
    else:
        tags = "、".join(detail_data["tags"])
        level = detail_data["attrs"]["role_level"]
        equip = detail_data["attrs"]["role_equipment_point"]
        experience = detail_data["attrs"]["role_experience_point"]
        sect = detail_data["attrs"]["role_sect"]
        camp = detail_data["attrs"]["role_camp"]
        shape = detail_data["attrs"]["role_shape"]
        msg = f"商品名称：{product}\n售卖者：{seller_full_info}\n点赞：{follower_count}\n剩余时间：{remain}\n标签：{tags}\n价格：{price}\n体型：{sect} - {camp} - {shape}\n装备分数：{level}级 - {equip}\n资历：{experience}"
        return msg