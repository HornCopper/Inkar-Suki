from jinja2 import Template

from src.const.jx3.server import Server
from src.const.jx3.school import School
from src.templates import HTMLSourceCode
from src.utils.network import Request
from src.utils.generate import generate

from ._template import zlrank_template_body, zlrank_table_head

async def get_zlrank(server: str, school: str):
    params = {
        "cursor": 0,
        "size": 50,
        "gameVersion": 0,
        "zoneName": Server(server).zone or "",
        "serverName": server or "",
        "forceId": School(school).internel_id or -1,
    }
    data = (await Request("https://m.pvp.xoyo.com/user/list-jx3-topn-roles-info", params=params).post(tuilan=True)).json()
    tables = []
    num = 0
    for person in data["data"]["roles"]:
        person: dict
        num += 1
        tables.append(
            Template(zlrank_template_body).render(
                rank = str(num),
                avatar = person["avatarUrl"] or "https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/Unknown.png",
                nickname = person["nickName"],
                role = person["roleName"] + "·" + person["serverName"],
                value = str(person["Value"])
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = f" 资历排行 · {server or '全服'} · {school or '全门派'}",
            table_head = zlrank_table_head,
            table_body = "\n".join(tables)
        )
    )
    image = await generate(html, "table", segment=True)
    return image