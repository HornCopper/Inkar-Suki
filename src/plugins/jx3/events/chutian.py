from pathlib import Path
from jinja2 import Template

from src.config import Config
from src.utils.network import Request
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from ._template import template_chutian, table_chutian_head

async def get_chutian_image():
    url = f"{Config.jx3.api.url}/data/active/celebs?name=楚天社"
    data = (await Request(url).get()).json()
    tables = []
    for i in data["data"]:
        time = i["time"]
        icon = i["icon"] if i["icon"] != "10" else "12"
        icon = "https://img.jx3box.com/pve/minimap/minimap_" + icon + ".png"
        desc = i["desc"]
        section = i["event"]
        map = i["map_name"]
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
            application_name = " · 楚天社 · " + Time().format("%H:%M:%S"),
            table_head = table_chutian_head,
            table_body = "\n".join(tables)
        )
    )
    final_path = await generate(html, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()