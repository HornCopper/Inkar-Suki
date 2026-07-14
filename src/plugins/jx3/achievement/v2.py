from jinja2 import Template
from pathlib import Path

from src.const.path import (
    TEMPLATES,
    build_path
)
from src.const.prompts import PROMPT
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.database.player import search_player
from src.templates import HTMLSourceCode
from src.plugins.jx3.detail.detail import (
    ACHIEVEMENT_API,
    load_achievement_table,
    load_detail_names,
    parse_completed_ids,
)

from ._template import table_head, template_body


async def _get_completed_achievement_ids(
    global_role_id: str,
) -> tuple[set[int] | None, str]:
    try:
        response = await Request(
            ACHIEVEMENT_API,
            params={"jx3id": global_role_id},
        ).get(timeout=20)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return None, "成就数据请求失败，请稍后再试。"
    if payload.get("code") != 0 or not isinstance(payload.get("data"), dict):
        return None, payload.get("msg") or "暂未查询到该角色的成就数据。"
    return parse_completed_ids(payload["data"].get("achievements")), ""


def _render_achievement_rows(
    achievements: list[dict],
    completed_ids: set[int],
) -> str:
    detail_names = load_detail_names()
    contents = []
    for achievement in achievements:
        finished = achievement["id"] in completed_ids
        contents.append(
            Template(template_body).render(
                image=(
                    f'https://icon.jx3box.com/icon/{achievement["icon_id"]}.png'
                    if achievement["icon_id"]
                    else ""
                ),
                name=achievement["name"],
                type=detail_names.get(achievement["detail"], "未知"),
                desc=achievement["desc"] or achievement["short_desc"],
                value=achievement["points"],
                status="correct" if finished else "incorrect",
                flag="✔" if finished else "✖",
                current=1 if finished else 0,
                target=1,
                progress=100 if finished else 0,
            )
        )
    return "\n".join(contents)

async def get_progress_v2(
    server: str = "", 
    name: str = "", 
    achievement: str = ""
):
    role_info = await search_player(role_name=name, server_name=server)
    guid = role_info.globalRoleId
    if not guid:
        return PROMPT.PlayerNotExist
    completed_ids, error = await _get_completed_achievement_ids(guid)
    if completed_ids is None:
        return error

    keyword = achievement.casefold()
    data = [
        item
        for item in load_achievement_table()
        if keyword
        in "".join(
            (item["name"], item["short_desc"], item["desc"])
        ).casefold()
    ][:200]
    if not data:
        return "唔……未找到相关成就。"

    html = str(
        HTMLSourceCode(
            application_name=f"成就百科 · [{name}·{server}] · {achievement}",
            additional_css=Path(
                build_path(TEMPLATES, ["jx3", "achievements_v2.css"])
            ).as_uri(),
            table_head=table_head,
            table_body=_render_achievement_rows(data, completed_ids),
        )
    )
    return await generate(html, ".container", segment=True)

async def zone_achievement(
        server: str = "", 
        name: str = "", 
        zone: str = "", 
        mode: str = ""
    ):
    role_info = await search_player(role_name=name, server_name=server)
    guid = role_info.globalRoleId
    if not guid:
        return PROMPT.PlayerNotExist
    completed_ids, error = await _get_completed_achievement_ids(guid)
    if completed_ids is None:
        return error
    data = _select_dungeon_achievements(zone, mode)
    if not data:
        return "唔……未找到相关成就。"

    html = str(
        HTMLSourceCode(
            application_name=f"成就百科 · [{name}·{server}] · {mode}{zone}",
            additional_css=Path(
                build_path(TEMPLATES, ["jx3", "achievements_v2.css"])
            ).as_uri(),
            table_head=table_head,
            table_body=_render_achievement_rows(data, completed_ids),
        )
    )
    return await generate(html, ".container", segment=True)


def _select_dungeon_achievements(zone: str, mode: str) -> list[dict]:
    groups: dict[int, list[dict]] = {}
    for achievement in load_achievement_table():
        if achievement["general"] != 1 or achievement["sub"] != 11:
            continue
        map_id = achievement["map_id"]
        if map_id <= 0:
            continue
        text = "".join(
            (
                achievement["name"],
                achievement["short_desc"],
                achievement["desc"],
            )
        )
        if zone in text:
            groups.setdefault(map_id, []).append(achievement)

    if not groups:
        return []

    target = mode + zone
    for achievements in groups.values():
        if any(
            target
            in "".join((item["name"], item["short_desc"], item["desc"]))
            for item in achievements
        ):
            return achievements

    for achievements in groups.values():
        if any(
            mode in "".join((item["name"], item["short_desc"], item["desc"]))
            for item in achievements
        ):
            return achievements

    if mode == "10人普通":
        mode_markers = (
            "5人普通",
            "5人英雄",
            "10人英雄",
            "10人挑战",
            "25人普通",
            "25人英雄",
            "25人挑战",
        )
        for achievements in groups.values():
            text = "".join(
                item["name"] + item["short_desc"] + item["desc"]
                for item in achievements
            )
            if not any(marker in text for marker in mode_markers):
                return achievements
    return []
