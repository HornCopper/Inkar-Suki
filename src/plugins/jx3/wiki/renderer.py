from src.tools.dep import *

async def render_items(keyword: str, data: dict, template: str = "question"):
    """
    渲染萌新接引
    """
    submit = {"keyword": keyword}
    submit.update(data)
    img = await get_render_image(f"src/views/jx3/wiki/{template}.html", submit, delay=200)
    return img
