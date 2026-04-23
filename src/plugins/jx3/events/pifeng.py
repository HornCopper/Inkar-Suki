from jinja2 import Template

from src.config import Config
from src.utils.network import Request
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from ._template import template_chutian, table_chutian_head

async def get_pifeng_image():
    url = f"{Config.jx3.api.url}/data/active/celebs"
    params = {
        "name": "披风会"
    }
    data = (await Request(url, params=params).get()).json()
    tables = []
    for i in data["data"]:
        time = i["time"]
        icon = i["icon"] if i["icon"] != "10" else "12"
        icon = "https://img.jx3box.com/pve/minimap/minimap_" + icon + ".png"
        desc = i["desc"]
        section = i["stage"]
        map = i["map"]
        site = i["site"]
        tables.append(
            Template(template_chutian).render(
                time = time,
                site = map + "·" + site,
                icon = icon,
                desc = desc,
                section = section
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = "披风会 · " + Time().format("%H:%M:%S"),
            table_head = table_chutian_head,
            table_body = "\n".join(tables)
        )
    )
    image = await generate(html, ".container", segment=True)
    return image