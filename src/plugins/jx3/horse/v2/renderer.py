from ..api_lib import *


async def render_items(server, horse_record: dict, map_data: dict, horse_data: dict, template: str = "horse_list"):
    """
    渲染马场
    """
    data = {
        'records': horse_record,
        'map_data': map_data,
        'horse_data': horse_data,
        'server': server,
        "config": {
            "horse": {
                "background": HorseInfo.from_id('background').to_dict()
            }
        },
        # 'command': command.to_dict() # TODO 注入使用说明
    }
    img = await get_render_image(
        f"src/views/jx3/horse/{template}.html",
        data, delay=200
    )
    return img
