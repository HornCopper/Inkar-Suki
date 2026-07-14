from jinja2 import Template

from src.config import Config
from src.plugins.jx3.trade.parsers import coin_to_image
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.time import Time

from ._template import bad, good, table_dilu_head, template_dilu


async def get_dilu_records(server: str = ""):
    params = {"token": Config.jx3.api.token_v2}
    if server:
        params["server"] = server
    data = (await Request(f"{Config.jx3.api.url}/data/steed/records", params=params).get()).json()

    if data["code"] != 200 or not data["data"]:
        return "未找到相关的卢记录，请检查服务器后重试！"

    records = data["data"] if server else [record["data"] for record in data["data"]]
    camp_icons = {"浩气盟": good, "恶人谷": bad, "中立": ""}
    rows = []
    for record in records:
        price = record["auction_amount"]
        if "万" in price:
            brick, gold = price.split("万", maxsplit=1)
            gold = gold.removesuffix("金")
            price = f"{brick}砖"
            if gold:
                price += f"{gold}金"
        rows.append(
            Template(template_dilu).render(
                server=record["server"],
                flush=Time(record["refresh_time"]).format(),
                captured=Time(record["capture_time"]).format(),
                sell=Time(record["auction_time"]).format(),
                map=record["map_name"],
                capturer=record["capture_role_name"],
                ci=camp_icons[record["capture_camp_name"]],
                cc=record["capture_camp_name"],
                auctioner=record["auction_role_name"],
                bi=camp_icons[record["auction_camp_name"]],
                bc=record["auction_camp_name"],
                price=coin_to_image(price),
            )
        )

    html = str(
        HTMLSourceCode(
            application_name=f"的卢统计 · {server or '全服'}",
            table_head=table_dilu_head,
            table_body="\n".join(rows),
        )
    )
    return await generate(html, ".container", segment=True)
