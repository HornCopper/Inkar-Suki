from jinja2 import Template
from nonebot.adapters.onebot.v11 import Message

from src.config import Config
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.network import Request


GAME_RANK_NAMES = (
    "名士五十强",
    "老江湖五十强",
    "兵甲藏家五十强",
    "名师五十强",
    "阵营英雄五十强",
    "薪火相传五十强",
    "庐园广记一百强",
    "浩气神兵宝甲五十强",
    "恶人神兵宝甲五十强",
    "浩气爱心帮会五十强",
    "恶人爱心帮会五十强",
    "赛季恶人五十强",
    "赛季浩气五十强",
    "上周恶人五十强",
    "上周浩气五十强",
    "本周恶人五十强",
    "本周浩气五十强",
)

FIELD_NAMES = (
    ("server", "服务器"),
    ("camp_name", "阵营"),
    ("role_name", "角色"),
    ("tong_name", "帮会"),
    ("master_name", "帮主"),
    ("force_name", "门派"),
    ("castle_name", "据点"),
    ("role_level", "等级"),
    ("now_count", "当前数量"),
    ("max_count", "最大数量"),
    ("total_score", "积分"),
)

TABLE_HEAD = """<th class="short-column">排名</th>
{% for column in columns %}<th class="short-column">{{ column }}</th>{% endfor %}"""
TABLE_ROW = """<tr><td class="short-column">{{ rank }}</td>
{% for value in values %}<td class="short-column">{{ value }}</td>{% endfor %}</tr>"""


async def get_game_rank(server: str, rank_name: str):
    params = {"name": rank_name, "token": Config.jx3.api.token}
    if server:
        params["server"] = server
    response = (await Request(f"{Config.jx3.api.url}/data/rank/statistics", params=params).get()).json()
    if response["code"] != 200 or not response["data"]:
        return "未找到该榜单的数据，请检查服务器和榜单名称后重试！"

    groups = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    records = []
    for group in groups:
        for rank, record in enumerate(group["data"], 1):
            item = dict(record)
            if "server" not in item:
                item["server"] = group["server"]
            item["rank"] = rank
            records.append(item)
    columns = [
        (field, label)
        for field, label in FIELD_NAMES
        if any(field in record for record in records)
    ]

    images = []
    pages = [records[index:index + 100] for index in range(0, len(records), 100)]
    for page_number, page in enumerate(pages, 1):
        rows = []
        for record in page:
            values = []
            for field, _ in columns:
                value = record[field] if field in record else "-"
                if field == "total_score" and isinstance(value, (int, float)):
                    value = f"{value:,}"
                values.append(value)
            rows.append(Template(TABLE_ROW).render(rank=record["rank"], values=values))
        page_suffix = f" · {page_number}/{len(pages)}" if len(pages) > 1 else ""
        html = str(
            HTMLSourceCode(
                application_name=f"江湖榜单 · {server or '全服'} · {rank_name}{page_suffix}",
                table_head=Template(TABLE_HEAD).render(columns=[label for _, label in columns]),
                table_body="".join(rows),
            )
        )
        images.append(await generate(html, ".container", segment=True))
    return Message(images)
