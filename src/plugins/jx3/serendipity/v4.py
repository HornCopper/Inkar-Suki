from collections import Counter
from datetime import datetime
from pathlib import Path
from random import choice

from jinja2 import Template

from src.config import Config
from src.const.jx3.school import School
from src.const.path import ASSETS, build_path
from src.const.prompts import PROMPT
from src.templates import SimpleHTML
from src.utils.database.player import search_player
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.time import Time

from .without_jx3api import JX3Serendipity


CARD_TEMPLATE = """
<article class="event-card {{ category }}{% if not triggered %} untriggered{% endif %}">
    {% if month_label %}<span class="month-label">{{ month_label }}</span>{% endif %}
    <div class="ink-circle">
        {% if show_path %}<img class="event-art" src="{{ show_path }}" alt="{{ event_name }}">{% endif %}
        {% if name_path %}<img class="event-name" src="{{ name_path }}" alt="{{ event_name }}">{% else %}<span class="event-name-text">{{ event_name }}</span>{% endif %}
        {% if peerless_icon %}<img class="peerless-badge" src="{{ peerless_icon }}" alt="绝世">{% endif %}
    </div>
    {% if not triggered %}<img class="attempted-icon" src="{{ attempted_icon }}" alt="已尝试">{% endif %}
    <div class="event-time">{{ time }}</div>
    {% if relative_time %}<div class="relative-time">{{ relative_time }}</div>{% endif %}
</article>
"""


def _catalogue() -> list[dict]:
    result = []
    for level, category in (
        (1, "common"),
        (2, "peerless"),
    ):
        directory = Path(build_path(
            ASSETS, ["image", "jx3", "serendipity", "serendipity", category]
        ))
        result.extend(
            {"name": path.stem, "level": level, "category": category}
            for path in directory.glob("*.png")
        )
    return result


def _show_path(name: str, category: str, school: str) -> str:
    directory = Path(build_path(
        ASSETS, ["image", "jx3", "serendipity", "show", category]
    ))
    school_path = directory / f"{name}-{school}.png"
    if school and school_path.is_file():
        return school_path.as_posix()

    generic_path = directory / f"{name}.png"
    if generic_path.is_file():
        return generic_path.as_posix()

    variants = list(directory.glob(f"{name}-*.png"))
    return choice(variants).as_posix() if variants else ""


async def get_serendipity_image_v4(server: str, name: str):
    player = await search_player(role_name=name, server_name=server)
    if not player.roleId:
        return PROMPT.PlayerNotExist

    if Config.jx3.api.enable:
        response = await Request(
            f"{Config.jx3.api.url}/data/event/records",
            params={"server": server, "name": name, "token": Config.jx3.api.token},
        ).get()
        payload = response.json()
        records = await JX3Serendipity().merge_api_with_my_data(
            payload.get("data") or [], server, name, player.globalRoleId, player.roleId
        )
    else:
        records = await JX3Serendipity().integration(
            server, name, player.roleId, player.globalRoleId
        )

    record_map = {
        (item.get("event") or item.get("name")): item
        for item in records
        if item.get("event") or item.get("name")
    }
    catalogue = _catalogue()
    # Dated records are newest-first, completed records with an unknown date
    # follow, and never-triggered entries remain together at the bottom.
    catalogue.sort(
        key=lambda item: (
            1 if item["name"] in record_map else 0,
            int(record_map.get(item["name"], {}).get("time") or 0),
            item["name"],
        ),
        reverse=True,
    )

    school = School(player.forceName).name or player.forceName
    name_directory = Path(build_path(ASSETS, ["image", "jx3", "serendipity", "name"]))
    month_counts = Counter()
    for item in catalogue:
        timestamp = int(record_map.get(item["name"], {}).get("time") or 0)
        if timestamp:
            date = datetime.fromtimestamp(timestamp)
            month_counts[(date.year, date.month)] += 1

    cards = []
    handled_months = set()
    first_dated_record = True
    for item in catalogue:
        record = record_map.get(item["name"])
        timestamp = int(record.get("time") or 0) if record else 0
        if timestamp:
            time_text = Time(timestamp).format("%Y-%m-%d %H:%M:%S")
            relative_time = Time().relate(timestamp)
        elif record:
            time_text, relative_time = "遗忘的时间", ""
        else:
            time_text, relative_time = "尚未触发", "等待江湖相逢"
        name_path = name_directory / f"{item['name']}.png"
        month_label = ""
        if timestamp:
            date = datetime.fromtimestamp(timestamp)
            month = (date.year, date.month)
            if (
                (first_dated_record or month_counts[month] >= 2)
                and month not in handled_months
            ):
                month_label = f"{date.year}.{date.month}"
                handled_months.add(month)
            first_dated_record = False
        cards.append(Template(CARD_TEMPLATE).render(
            event_name=item["name"],
            category=item["category"],
            month_label=month_label,
            peerless_icon=(
                build_path(
                    ASSETS,
                    ["image", "jx3", "serendipity", "vector", "peerless.png"],
                )
                if item["category"] == "peerless"
                else ""
            ),
            triggered=record is not None,
            show_path=_show_path(item["name"], item["category"], school),
            name_path=name_path.as_posix() if name_path.is_file() else "",
            time=time_text,
            relative_time=relative_time,
            attempted_icon=build_path(
                ASSETS, ["image", "jx3", "serendipity", "vector", "attempted.png"]
            ),
        ))

    catalogue_names = {item["name"] for item in catalogue}
    triggered_count = len(catalogue_names.intersection(record_map))
    html = str(SimpleHTML(
        "jx3",
        "serendipity_v4.html",
        font=build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
        ink_background=build_path(
            ASSETS, ["image", "jx3", "serendipity", "vector", "background.png"]
        ),
        name=name,
        server=server,
        triggered=triggered_count,
        total=len(catalogue),
        cards="\n".join(cards),
        app_info=f"个人奇遇记录 · {server} · {name} · " + Time().format("%H:%M:%S"),
    ))
    return await generate(html, ".serendipity-panel", segment=True)
