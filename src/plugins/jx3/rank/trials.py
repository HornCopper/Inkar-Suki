from jinja2 import Template

from src.config import Config
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.network import Request

from ._template import slrank_table_head, slrank_template_body


async def get_slrank(school: str, server: str):
    params = {"name": school, "token": Config.jx3.api.token}
    if server:
        params["server"] = server
    data = (
        await Request(
            f"{Config.jx3.api.url}/data/rank/trials",
            params=params,
        ).get()
    ).json()
    groups = [data["data"]] if isinstance(data["data"], dict) else data["data"]
    records = [
        (group["server"], record)
        for group in groups
        for record in group["data"]
    ]
    if not server:
        records.sort(
            key=lambda item: (
                item[1]["max_level"],
                item[1]["total_score"],
                item[1]["equip_score"],
            ),
            reverse=True,
        )
        records = records[:50]

    rows = [
        Template(slrank_template_body).render(
            rank=rank,
            server=record_server,
            role_name=record["role_name"],
            level=record["max_level"],
            grade=f"{int(record['total_score']):,}",
            score=record["equip_score"],
        )
        for rank, (record_server, record) in enumerate(records, 1)
    ]
    html = str(
        HTMLSourceCode(
            application_name=f"试炼之地 · {server or '全服'} · {school}",
            table_head=slrank_table_head,
            table_body="\n".join(rows),
        )
    )
    return await generate(html, ".container", segment=True)
