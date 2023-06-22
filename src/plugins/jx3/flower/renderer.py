from src.tools.dep.api import *
async def renderer(server: str, data: list) -> str:
    img = await get_render_image('src/views/jx3/pvx/flower/index.html', {
        'data': data,
        'server': server,
    }, delay=200)
    return img
