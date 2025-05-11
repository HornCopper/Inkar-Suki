from typing import Literal, Any
from jinja2 import Template

from src.const.jx3.kungfu import Kungfu
from src.utils.network import Request
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from ._template import (
    rank_table_head,
    rank_template_body
)

name_to_pinyin = {
    "莫问": "mowen",
    "相知": "xiangzhi",
    "花间游": "huajianyou",
    "离经易道": "lijingyidao",
    "无方": "wufang",
    "灵素": "lingsu",
    "毒经": "dujing",
    "补天诀": "butianjue",
    "冰心诀": "bingxinjue",
    "云裳心经": "yunchangxinjing",
    "明尊琉璃体": "mingzunliuliti",
    "焚影圣诀": "fenyingshengjue",
    "铁牢律": "tielaolv",
    "傲血战意": "aoxuezhanyi",
    "洗髓经": "xisuijing",
    "易筋经": "yijinjing",
    "分山劲": "fenshanjin",
    "铁骨衣": "tieguyi",
    "紫霞功": "zixiagong",
    "太虚剑意": "taixujianyi",
    "惊羽诀": "jingyujue",
    "天罗诡道": "tianluoguidao",
    "太玄经": "taixuanjing",
    "问水诀": "wenshuijue",
    "笑尘诀": "xiaochenjue",
    "北傲诀": "beiaojue",
    "凌海诀": "linghaijue",
    "隐龙诀": "yinlongjue",
    "孤锋诀": "gufengjue",
    "山海心诀": "shanhaixinjue",
    "周天功": "zhoutiangong"
}

async def get_rank(dungeon_full_name: str, boss_name: str, kungfu_name: str, order_by: Literal["rdps", "rhps"] = "rdps"):
    url = "http://116.211.150.188:8009/getRank"
    params = {
        "map": dungeon_full_name,
        "boss": boss_name,
        "occ": name_to_pinyin[kungfu_name],
        "page": 1,
        "orderby": order_by
    }
    data: dict[str, Any] = (await Request(url, params=params).get()).json()
    if data["result"]["num"] == 0:
        return "未找到相关数据，请检查首领名称！"
    tables = []
    rank = 1
    for record in data["result"]["table"][:20]:
        tables.append(
            Template(rank_template_body).render(
                rank = str(rank),
                kungfu_icon = Kungfu(kungfu_name).icon,
                name = record["id"],
                server = record["server"],
                value = str(int(record[order_by]))
            )
        )
        rank += 1
    html = str(
        HTMLSourceCode(
            application_name = f" · 门派天梯 · {dungeon_full_name} · {boss_name}",
            table_head = rank_table_head,
            table_body = "\n".join(tables)
        )
    )
    image = await generate(html, "table", segment=True)
    return image