from src.tools.dep import *


async def renderer(server: str, arg_map: str, arg_species: str, data: list) -> str:
    args = {
        "data": data,
        "server": server,
        "map": arg_map,
        "species": arg_species
    }
    img = await get_render_image("src/views/jx3/pvx/flower/index.html", args)
    return img
