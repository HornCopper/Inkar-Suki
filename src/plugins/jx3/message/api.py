from html import escape

from jinja2 import Template

from src.config import Config
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.time import Time

from ._template import (
    chat_records_css,
    template_chat_record,
    template_chat_records_head,
)

async def get_chat_records(server: str, name: str, page: int = 1, limit: int = 20):
    url = f"{Config.jx3.api.url}/chat/records"
    params = {
        "token": Config.jx3.api.token_v2 or Config.jx3.api.token,
        "server": server,
        "name": name,
        "page": page,
        "limit": limit,
    }
    data = (await Request(url, params = params).get()).json()
    if data["code"] != 200:
        return data["msg"] or "聊天记录查询失败，请稍后重试！"

    detail = data["data"]
    records = detail["list"]
    if not records:
        return "未找到该角色的聊天记录，请检查区服和角色名！"

    table = []
    for index, record in enumerate(records, start = (page - 1) * limit + 1):
        channel = str(record["channel"] or "未知")
        role_name = str(record["roleName"] or name)
        message = str(record["message"] or "（空消息）")
        for prefix in (f"[{channel}][{role_name}]：", f"[{channel}][{role_name}]:"):
            if message.startswith(prefix):
                message = message[len(prefix):].lstrip()
                break
        table.append(
            Template(template_chat_record).render(
                index = index,
                time = Time(record["time"] or 0).format("%Y-%m-%d %H:%M:%S"),
                channel = escape(channel),
                message = escape(message),
            ),
        )

    total = int(detail["total"] or len(records))
    total_pages = (total + limit - 1) // limit
    html = str(
        HTMLSourceCode(
            application_name = f"聊天记录 · [{name}·{server}]",
            footer = f"第 {page}/{total_pages} 页 · 本页 {len(records)} 条 · 共 {total} 条",
            additional_css = chat_records_css,
            table_head = template_chat_records_head,
            table_body = "\n".join(table),
        ),
    )
    return await generate(html, ".container", segment = True)
