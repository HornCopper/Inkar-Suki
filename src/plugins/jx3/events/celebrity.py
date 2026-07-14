from datetime import datetime, timedelta

from jinja2 import Template

from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.time import Time

from ._template import table_chutian_head, template_chutian


async def get_celebrity_image(name: str, celebrity_type: int, cycle_hours: int):
    data = (
        await Request(
            "https://cms.jx3box.com/api/cms/game/celebrity",
            params={"type": celebrity_type},
        ).get()
    ).json()
    now = datetime.now()
    cycle_minutes = cycle_hours * 60
    current_offset = (now.hour % cycle_hours) * 60 + now.minute
    records = []
    for record in data["data"]:
        if celebrity_type == 0:
            event_hours = [int(record["key"][1:], 2)]
        elif celebrity_type == 1 and record["key"] in {"y0", "y1"}:
            event_hours = list(range(int(record["key"][1:]), cycle_hours, 2))
        else:
            event_hours = [record["hour"] or 0]
        for event_hour in event_hours:
            event_offset = event_hour * 60 + record["time"]
            delta = (event_offset - current_offset) % cycle_minutes
            records.append((delta, record))
    records.sort(key=lambda item: item[0])

    tables = []
    for delta, record in records[:10]:
        event_time = now + timedelta(minutes=delta)
        icon = record["icon"] if record["icon"] != "10" else "12"
        tables.append(
            Template(template_chutian).render(
                time=event_time.strftime("%H:%M"),
                site=record["map"] + "·" + record["site"],
                icon=f"https://img.jx3box.com/pve/minimap/minimap_{icon}.png",
                desc=record["desc"],
                section=record["stage"],
            )
        )
    html = str(
        HTMLSourceCode(
            application_name=f"{name} · {Time().format('%H:%M:%S')}",
            table_head=table_chutian_head,
            table_body="\n".join(tables),
        )
    )
    return await generate(html, ".container", segment=True)
