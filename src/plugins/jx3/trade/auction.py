from jinja2 import Template

from src.config import Config
from src.const.path import ASSETS, build_path
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.time import Time

from .parsers import coin_to_image
from ._template import template_auction, template_auction_head


async def get_auction_image(server: str, name: str = ""):
    params = {
        "server": server,
        "name": name,
        "limit": 50,
        "token": Config.jx3.api.token_v2,
    }
    data = (await Request(f"{Config.jx3.api.url}/data/auction/records",params=params,).get()).json()

    if data["code"] != 200:
        return "未找到相关记录，请检查物品名称！"

    records = data["data"]
    if not records:
        suffix = f"中包含「{name}」的" if name else ""
        return f"唔……没有找到{server}{suffix}阵营拍卖记录。"

    rows = []
    for record in records:
        price = record["item_amount"]
        if "万" in price:
            brick, gold = price.split("万", maxsplit=1)
            gold = gold.removesuffix("金")
            price = f"{brick}砖"
            if gold:
                price += f"{gold}金"
        camp_icon = build_path(
            ASSETS,
            [
                "image",
                "jx3",
                "camp",
                "haoqi.png" if record["camp_name"] == "浩气盟" else "eren.png",
            ],
        )
        rows.append(
            Template(template_auction).render(
                camp_icon=camp_icon,
                camp_name=record["camp_name"],
                role_name=record["role_name"],
                item_name=record["item_name"],
                item_amount=coin_to_image(price),
                time=Time(record["time"]).format(),
            )
        )

    html = str(
        HTMLSourceCode(
            application_name=(
                f"阵营拍卖 · {server} · {name}"
                if name
                else f"阵营拍卖 · {server}"
            ),
            table_head=template_auction_head,
            table_body="\n".join(rows),
        )
    )
    return await generate(html, ".container", segment=True)
