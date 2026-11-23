from jinja2 import Template
from nonebot.adapters.onebot.v11 import Message

from src.config import Config
from src.const.jx3.school import School
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.jx3api import jx3api_get

GAME_RANK_GROUPS = {
    "/rank/records": (
        "名士五十强", "老江湖五十强", "兵甲藏家五十强", "名师五十强", "薪火相传五十强", "庐园广记一百强",
        "恶人后勤一百强", "浩气后勤一百强", "恶人英雄五十强", "浩气英雄五十强", "本周恶人一百强", "本周浩气一百强",
    ),
    "/rank/guild": (
        "浩气神兵宝甲五十强", "恶人神兵宝甲五十强", "浩气爱心帮会五十强", "恶人爱心帮会五十强",
        "赛季恶人五十强", "赛季浩气五十强", "上周恶人五十强", "上周浩气五十强", "本周恶人五十强", "本周浩气五十强",
    ),
    "/rank/castle": (
        "不空关", "世外坡", "凛风堡", "凤鸣堡", "千岩关", "卧龙坡", "啖杏林", "大理山城", "惊虬谷", "扶风郡",
        "日月崖", "枫湖寨", "武王城", "澜沧城", "激流坞", "烈日岗", "盘龙坞", "神池岭", "秋雨堡", "红莲岗",
        "逐鹿坪", "金门关", "霜戈堡", "青云坞", "飞沙关", "龙门镇",
    ),
    "/rank/battle": ("绝境名士录", "龙门天命榜", "荒漠霸王榜", "独步尊者榜", "喋血枭雄录", "佛系圣手榜", "瀚海兵甲榜"),
}
GAME_RANK_PATHS = {name: path for path, names in GAME_RANK_GROUPS.items() for name in names}
GAME_RANK_NAMES = tuple(GAME_RANK_PATHS)

FIELD_NAMES = (
    ("server", "服务器"),
    ("campName", "阵营"),
    ("name", "角色"),
    ("tongName", "帮会"),
    ("masterName", "帮主"),
    ("forceName", "门派"),
    ("castleName", "据点"),
    ("level", "等级"),
    ("nowCount", "当前数量"),
    ("maxCount", "最大数量"),
    ("totalScore", "积分"),
    ("contribution", "贡献"),
    ("battleRounds", "场次"),
    ("kills", "总击杀"),
    ("assists", "总助攻"),
    ("wins", "夺冠次数"),
)

RANK_FIELD_ALIASES = {
    "campName": ("szCampName",),
    "name": ("szName", "roleName"),
    "tongName": ("szTongName",),
    "masterName": ("szMasterName",),
    "forceName": ("szForceName",),
    "castleName": ("szCastleName",),
    "level": ("nLevel", "byLevel"),
    "nowCount": ("nMemberCount",),
    "maxCount": ("nMaxMemberCount",),
    "totalScore": ("nScore", "nTotalPoint", "MATCH_LEVEL"),
    "contribution": ("nContribution",),
    "battleRounds": ("BATTLE_ROUNDS",),
    "kills": ("SUM_KILL_COUNT",),
    "assists": ("SUM_ASSIST_KILL_COUNT",),
    "wins": ("TOP_COUNT",),
}

def normalize_rank_record(record: dict) -> dict:
    """Map client field names while retaining support for older proxy data."""
    item = dict(record)
    for field, aliases in RANK_FIELD_ALIASES.items():
        if item.get(field) is not None:
            continue
        for alias in aliases:
            if record.get(alias) is not None:
                item[field] = record[alias]
                break
    if not item.get("forceName") and "byForceID" in record:
        school = School.with_internel_id(record["byForceID"]).name
        if school:
            item["forceName"] = school
    return item

TABLE_HEAD = """<th class="short-column">排名</th>
{% for column in columns %}<th class="short-column">{{ column }}</th>{% endfor %}"""
TABLE_ROW = """<tr><td class="short-column">{{ rank }}</td>
{% for value in values %}<td class="short-column">{{ value }}</td>{% endfor %}</tr>"""

async def get_game_rank(server: str, rank_name: str):
    if rank_name not in GAME_RANK_PATHS:
        return "榜单名称无效，可查询：\n" + "、".join(GAME_RANK_NAMES)
    params = {"name": rank_name, "token": Config.jx3.api.token}
    if server:
        params["server"] = server
    response = await jx3api_get(GAME_RANK_PATHS[rank_name], params = params)
    if response["code"] != 200 or not response["data"]:
        return response["msg"] or "未找到该榜单的数据，请检查服务器和榜单名称后重试！"

    groups = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    records = []
    for group in groups:
        for rank, record in enumerate(group["data"], 1):
            item = normalize_rank_record(record)
            if "server" not in item:
                item["server"] = group.get("server") or server or "-"
            item["rank"] = record.get("rank", record.get("nRank", rank))
            records.append(item)
    if not records:
        return "未找到该榜单的数据，请检查服务器和榜单名称后重试！"
    rank_label = groups[0].get("label") or rank_name
    columns = [(field, label) for field, label in FIELD_NAMES if any(field in record for record in records)]

    images = []
    pages = [records[index:index + 100] for index in range(0, len(records), 100)]
    for page_number, page in enumerate(pages, 1):
        rows = []
        for record in page:
            values = []
            for field, _ in columns:
                value = record[field] if field in record else "-"
                if field in {"totalScore", "contribution", "kills", "assists"} and isinstance(value, (int, float)):
                    value = f"{value:,}"
                values.append(value)
            rows.append(Template(TABLE_ROW).render(rank = record["rank"], values = values))
        page_suffix = f" · {page_number}/{len(pages)}" if len(pages) > 1 else ""
        html = str(
            HTMLSourceCode(
                application_name = f"江湖榜单 · {server or '全服'} · {rank_label}{page_suffix}",
                table_head = Template(TABLE_HEAD).render(columns = [label for _, label in columns]),
                table_body = "".join(rows),
            ),
        )
        images.append(await generate(html, ".container", segment = True))
    return Message(images)
