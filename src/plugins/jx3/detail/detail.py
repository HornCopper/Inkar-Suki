from functools import lru_cache
from typing import Any, Iterable

from jinja2 import Template

from src.const.path import ASSETS, build_path
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.database.tabs import read_tab

from ._template import global_view_head, template_global_view


ACHIEVEMENT_API = "https://next2.jx3box.com/api/next2/user-achievements"
ACHIEVEMENT_TABLE = build_path(
    ASSETS, ["source", "jx3", "tabs", "achievement", "Achievement.txt"]
)
ACHIEVEMENT_SUB_TABLE = build_path(
    ASSETS,
    ["source", "jx3", "tabs", "achievement", "AchievementSub.txt"],
)
ACHIEVEMENT_DETAIL_TABLE = build_path(
    ASSETS,
    ["source", "jx3", "tabs", "achievement", "AchievementDetails.txt"],
)
ACHIEVEMENT_POINTS_TABLE = build_path(
    ASSETS,
    ["source", "jx3", "tabs", "achievement", "AchievementPoints.txt"],
)

VIEW_GLOBAL = "全局总览"
VIEW_MAP = "地图总览"
VIEW_TOP = "五甲总览"
VIEW_GLOBAL_WITH_TOP = "全局总览(含五甲)"
VIEW_DUNGEON = "秘境总览"
VIEW_TYPES = [
    VIEW_GLOBAL,
    VIEW_MAP,
    VIEW_TOP,
    VIEW_GLOBAL_WITH_TOP,
    VIEW_DUNGEON,
]


def load_tab_dicts(path: str) -> list[dict[str, str]]:
    table = read_tab(path)
    if not table:
        return []
    header, *rows = table
    return [
        dict(zip(header, row + [""] * (len(header) - len(row))))
        for row in rows
    ]


@lru_cache(maxsize=1)
def load_sub_names() -> dict[int, str]:
    names: dict[int, str] = {}
    for row in load_tab_dicts(ACHIEVEMENT_SUB_TABLE):
        try:
            names[int(row["ID"])] = row["Name"]
        except (KeyError, TypeError, ValueError):
            continue
    return names


@lru_cache(maxsize=1)
def load_detail_names() -> dict[int, str]:
    names: dict[int, str] = {}
    for row in load_tab_dicts(ACHIEVEMENT_DETAIL_TABLE):
        try:
            names[int(row["ID"])] = row["Name"]
        except (KeyError, TypeError, ValueError):
            continue
    return names


@lru_cache(maxsize=1)
def load_achievement_points() -> dict[int, int]:
    points: dict[int, int] = {}
    for row in load_tab_dicts(ACHIEVEMENT_POINTS_TABLE):
        try:
            points[int(row["ID"])] = int(row["RewardPoint"])
        except (KeyError, TypeError, ValueError):
            continue
    return points


@lru_cache(maxsize=1)
def load_achievement_table() -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    achievement_points = load_achievement_points()
    for row in load_tab_dicts(ACHIEVEMENT_TABLE):
        try:
            achievement_id = int(row["ID"])
            general = int(row["General"])
            sub = int(row["Sub"])
            detail = int(row.get("Detail") or 0)
        except (KeyError, TypeError, ValueError):
            continue
        if (
            achievement_id <= 0
            or row.get("Visible") != "1"
            or general <= 0
            or sub <= 0
        ):
            continue
        records.append(
            {
                "id": achievement_id,
                "general": general,
                "sub": sub,
                "detail": detail,
                "name": row.get("Name", ""),
                "short_desc": row.get("ShortDesc", ""),
                "desc": row.get("Desc", ""),
                "icon_id": int(row.get("IconID") or 0),
                "map_id": int(row.get("dwMapID") or 0),
                "points": achievement_points.get(achievement_id, 0),
            }
        )
    return tuple(records)


def parse_completed_ids(value: Any) -> set[int]:
    if not isinstance(value, str):
        return set()
    result: set[int] = set()
    for item in value.split(","):
        try:
            result.add(int(item))
        except ValueError:
            continue
    return result


def build_distribution(
    completed_ids: set[int],
    records: Iterable[dict[str, Any]],
    view: str = VIEW_GLOBAL,
) -> list[dict[str, Any]]:
    if view == VIEW_MAP:
        records = (
            record
            for record in records
            if record["general"] == 1 and record["sub"] == 8
        )
        category_field = "detail"
        category_names = load_detail_names()
    elif view == VIEW_TOP:
        records = (record for record in records if record["general"] == 2)
        category_field = "sub"
        category_names = load_sub_names()
    elif view == VIEW_GLOBAL_WITH_TOP:
        records = (record for record in records if record["general"] in (1, 2))
        category_field = "sub"
        category_names = load_sub_names()
    elif view == VIEW_DUNGEON:
        records = (
            record
            for record in records
            if record["general"] == 1 and record["sub"] == 11
        )
        category_field = "detail"
        category_names = load_detail_names()
    else:
        records = (record for record in records if record["general"] == 1)
        category_field = "sub"
        category_names = load_sub_names()

    categories: dict[int, dict[str, int]] = {}
    for achievement in records:
        category_id = achievement[category_field]
        if category_id <= 0:
            continue
        category = categories.setdefault(category_id, {"done": 0, "total": 0})
        points = achievement["points"]
        category["total"] += points
        if achievement["id"] in completed_ids:
            category["done"] += points

    result = []
    for category_id, values in categories.items():
        total = values["total"]
        done = values["done"]
        result.append(
            {
                "category_id": category_id,
                "subject": category_names.get(category_id, f"分类 {category_id}"),
                "done": done,
                "total": total,
                "ratio": done / total if total else 0,
            }
        )
    return sorted(result, key=lambda item: (-item["done"], item["category_id"]))


async def get_exp_info(
    server: str,
    name: str,
    global_role_id: str,
    view: str = VIEW_GLOBAL,
):
    try:
        response = await Request(
            ACHIEVEMENT_API,
            params={"jx3id": global_role_id},
        ).get(timeout=20)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return "资历数据请求失败，请稍后再试。"

    if payload.get("code") != 0 or not isinstance(payload.get("data"), dict):
        return payload.get("msg") or "暂未查询到该角色的资历数据。"

    completed_ids = parse_completed_ids(payload["data"].get("achievements"))
    distribution = build_distribution(completed_ids, load_achievement_table(), view)
    if not distribution:
        return "本地成就表为空，暂时无法生成资历分布。"

    tables = []
    for category in distribution:
        ratio = category["ratio"]
        tables.append(
            Template(template_global_view).render(
                subject=category["subject"],
                width=str(round(ratio * 100)),
                value=f'{category["done"]}/{category["total"]}',
            )
        )

    finished = sum(category["done"] for category in distribution)
    total = sum(category["total"] for category in distribution)
    ratio = finished / total if total else 0
    summary = Template(
        """
        <tr class="achievement-summary">
            <td colspan="3">
                <strong>{{ name }}</strong>
                <span class="summary-meta">· {{ server }} · {{ view }}</span>
                <span class="summary-value">{{ finished }}/{{ total }}（{{ percent }}%）</span>
            </td>
        </tr>
        """
    ).render(
        name=name,
        server=server,
        view=view,
        finished=finished,
        total=total,
        percent=round(ratio * 100),
    )
    html = str(
        HTMLSourceCode(
            application_name=f"资历分布 · [{name}·{server}] · {view}",
            table_head=global_view_head,
            table_body=summary + "\n" + "\n".join(tables),
            additional_css="""
                .container {
                    min-width: 0;
                    width: 820px;
                }
                .item-table {
                    min-width: 0;
                    width: 100%;
                }
                .item-table th:nth-child(1),
                .item-table td:nth-child(1) { min-width: 220px; }
                .item-table th:nth-child(2),
                .item-table td:nth-child(2) { min-width: 360px; }
                .item-table th:nth-child(3),
                .item-table td:nth-child(3) { min-width: 180px; }
                .achievement-summary td {
                    padding: 18px 22px;
                    background: #f8f9fa;
                    color: #2c3e50;
                    text-align: left;
                }
                .achievement-summary strong { font-size: 28px; }
                .summary-meta { margin-left: 8px; color: #667582; }
                .summary-value { float: right; color: #2c7be5; font-weight: 600; }
                .progress-bar { max-width: none; width: 300px; margin: 0 auto; }
                .progress { background: linear-gradient(90deg, #76c7c0, #4da7d8); }
            """,
        )
    )
    return await generate(html, ".container", segment=True)
