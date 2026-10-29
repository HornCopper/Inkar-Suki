from datetime import datetime, timedelta
from html import escape

from nonebot.adapters.onebot.v11 import MessageSegment

from src.templates import HTMLSourceCode
from src.utils.command import get_command_keys
from src.utils.database import logs_db
from src.utils.generate import generate

from ._template import (
    command_detail_head,
    command_statistics_css,
    command_summary_head,
)

def _day_start(value: datetime) -> datetime:
    return value.replace(hour = 0, minute = 0, second = 0, microsecond = 0)

def _format_timestamp(timestamp: int | None) -> str:
    if not timestamp:
        return "—"
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def _format_interval(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    if seconds < 60:
        return f"{seconds} 秒"
    if seconds < 3600:
        return f"{seconds // 60} 分 {seconds % 60} 秒"
    if seconds < 86400:
        return f"{seconds // 3600} 小时 {(seconds % 3600) // 60} 分"
    return f"{seconds // 86400} 天 {(seconds % 86400) // 3600} 小时"

def _available_command_keys() -> list[str]:
    database_keys = {
        str(row[0])
        for row in logs_db.fetch_all(
            "SELECT DISTINCT command_key FROM command_usage WHERE command_key != ''",
        )
    }
    return sorted(get_command_keys() | database_keys, key = str.casefold)

def _resolve_command_key(query: str, available_keys: list[str]) -> str | None:
    if query in available_keys:
        return query
    folded = [key for key in available_keys if key.casefold() == query.casefold()]
    return folded[0] if len(folded) == 1 else None

async def _render_image(
    application_name: str,
    table_head: str,
    table_body: str,
    footer: str,
) -> MessageSegment:
    source = str(
        HTMLSourceCode(
            application_name = application_name,
            table_head = table_head,
            table_body = table_body,
            additional_css = command_statistics_css,
            footer = footer,
        ),
    )
    return await generate(
        source,
        ".container",
        viewport = {
            "width": 1440,
            "height": 1080,
        },
        segment = True,
    )

async def _render_overview(available_keys: list[str], now: datetime) -> MessageSegment:
    today_start = int(_day_start(now).timestamp())
    seven_day_start = int((_day_start(now) - timedelta(days = 6)).timestamp())
    raw_rows = logs_db.fetch_all(
        """
        SELECT
            command_key,
            COUNT(*) AS total_count,
            SUM(CASE WHEN timestamp >= ? THEN 1 ELSE 0 END) AS today_count,
            SUM(CASE WHEN timestamp >= ? THEN 1 ELSE 0 END) AS seven_day_count,
            MAX(timestamp) AS last_timestamp
        FROM command_usage
        GROUP BY command_key
        """,
        today_start,
        seven_day_start,
    )
    statistics = {
        str(key): (int(total), int(today or 0), int(seven_days or 0), int(last or 0))
        for key, total, today, seven_days, last in raw_rows
    }
    rows = [(key, *statistics.get(key, (0, 0, 0, 0))) for key in available_keys]
    rows.sort(key = lambda row: (-row[1], row[0].casefold()))

    table_rows = []
    for rank, (key, total, today, seven_days, last) in enumerate(rows, start = 1):
        zero_class = " class=\"stats-zero\"" if total == 0 else ""
        table_rows.append(
            "<tr>"
            f"<td>{rank}</td>"
            f"<td class=\"stats-key-column\">{escape(key)}</td>"
            f"<td{zero_class}>{total}</td>"
            f"<td{zero_class}>{today}</td>"
            f"<td{zero_class}>{seven_days}</td>"
            f"<td class=\"stats-time-column{' stats-zero' if not last else ''}\">"
            f"{_format_timestamp(last)}</td>"
            "</tr>",
        )

    if not table_rows:
        table_rows.append(
            "<tr><td class=\"stats-message\" colspan=\"6\">暂无可统计的命令。</td></tr>",
        )

    total_calls = sum(row[1] for row in rows)
    return await _render_image(
        application_name = f"命令统计 · {len(rows)} 个命令 · 累计 {total_calls} 次",
        table_head = command_summary_head,
        table_body = "\n".join(table_rows),
        footer = f"统计范围：功能启用以来 · 更新于 {now:%Y-%m-%d %H:%M:%S}",
    )

async def _render_unknown_command(
    query: str,
    available_keys: list[str],
    now: datetime,
) -> MessageSegment:
    examples = "、".join(escape(key) for key in available_keys[:12]) or "暂无"
    body = (
        "<tr><td class=\"stats-message\">"
        f"未找到统计命令：{escape(query)}<br>"
        f"当前共有 {len(available_keys)} 个可统计命令。<br>"
        f"示例：{examples}"
        "</td></tr>"
    )
    return await _render_image(
        application_name = "命令统计 · 未找到命令",
        table_head = "<th>查询结果</th>",
        table_body = body,
        footer = f"更新于 {now:%Y-%m-%d %H:%M:%S}",
    )

async def _render_detail(command_key: str, now: datetime) -> MessageSegment:
    today = _day_start(now)
    today_start = int(today.timestamp())
    seven_day_start = int((today - timedelta(days = 6)).timestamp())
    thirty_day_start = int((today - timedelta(days = 29)).timestamp())
    aggregate = logs_db.fetch_all(
        """
        SELECT
            COUNT(*) AS total_count,
            SUM(CASE WHEN timestamp >= ? THEN 1 ELSE 0 END) AS today_count,
            SUM(CASE WHEN timestamp >= ? THEN 1 ELSE 0 END) AS seven_day_count,
            SUM(CASE WHEN timestamp >= ? THEN 1 ELSE 0 END) AS thirty_day_count,
            MIN(timestamp) AS first_timestamp,
            MAX(timestamp) AS last_timestamp
        FROM command_usage
        WHERE command_key = ?
        """,
        today_start,
        seven_day_start,
        thirty_day_start,
        command_key,
    )[0]
    total, today_count, seven_days, thirty_days, first, last = aggregate
    total = int(total or 0)
    today_count = int(today_count or 0)
    seven_days = int(seven_days or 0)
    thirty_days = int(thirty_days or 0)
    first = int(first or 0)
    last = int(last or 0)

    daily_rows = logs_db.fetch_all(
        """
        SELECT date(timestamp, 'unixepoch', 'localtime') AS day, COUNT(*)
        FROM command_usage
        WHERE command_key = ? AND timestamp >= ?
        GROUP BY day
        ORDER BY day ASC
        """,
        command_key,
        thirty_day_start,
    )
    daily_counts = {str(day): int(count) for day, count in daily_rows}
    daily_series = []
    for offset in range(30):
        day = today - timedelta(days = 29 - offset)
        day_text = day.strftime("%Y-%m-%d")
        daily_series.append((day_text, daily_counts.get(day_text, 0)))

    recent_timestamps = [
        int(row[0]) for row in logs_db.fetch_all(
            """
            SELECT timestamp
            FROM command_usage
            WHERE command_key = ?
            ORDER BY timestamp DESC, id DESC
            LIMIT 20
            """,
            command_key,
        )
    ]

    escaped_key = escape(command_key)
    cards = (
        "<tr class=\"stats-card-row\"><td colspan=\"4\">"
        "<div class=\"stats-cards\">"
        f'<div class="stats-card"><div class="stats-card-label">总调用</div><div class="stats-card-value">{total}</div></div>'
        f'<div class="stats-card"><div class="stats-card-label">今日</div><div class="stats-card-value">{today_count}</div></div>'
        f'<div class="stats-card"><div class="stats-card-label">近 7 日</div><div class="stats-card-value">{seven_days}</div></div>'
        f'<div class="stats-card"><div class="stats-card-label">近 30 日</div><div class="stats-card-value">{thirty_days}</div></div>'
        "</div>"
        f'<div class="stats-meta">首次调用：{_format_timestamp(first)}　·　最近调用：{_format_timestamp(last)}</div>'
        "</td></tr>"
    )

    max_daily = max((count for _, count in daily_series), default = 0)
    detail_rows = [cards, "<tr class=\"stats-section\"><td colspan=\"4\">近 30 日按日统计</td></tr>"]
    for index, (day, count) in enumerate(reversed(daily_series)):
        original_index = len(daily_series) - 1 - index
        previous = daily_series[original_index - 1][1] if original_index > 0 else None
        change = count - previous if previous is not None else None
        if change is None:
            change_text = "<span class=\"stats-muted\">—</span>"
        elif change > 0:
            change_text = f'<span class="stats-up">+{change}</span>'
        elif change < 0:
            change_text = f'<span class="stats-down">{change}</span>'
        else:
            change_text = "<span class=\"stats-muted\">0</span>"
        percentage = count / total * 100 if total else 0
        bar_width = count / max_daily * 100 if max_daily else 0
        detail_rows.append(
            "<tr>"
            f"<td>{day}</td>"
            f"<td>{count}</td>"
            f'<td><span class="stats-bar-track"><span class="stats-bar" style="display:block;width:{bar_width:.1f}%"></span></span> {percentage:.1f}%</td>'
            f"<td>{change_text}</td>"
            "</tr>",
        )

    detail_rows.append("<tr class=\"stats-section\"><td colspan=\"4\">最近 20 次调用</td></tr>")
    if recent_timestamps:
        for index, timestamp in enumerate(recent_timestamps, start = 1):
            older = recent_timestamps[index] if index < len(recent_timestamps) else None
            interval = timestamp - older if older is not None else None
            detail_rows.append(
                "<tr>"
                f"<td>#{index}</td>"
                f"<td>{_format_timestamp(timestamp)}</td>"
                f"<td>{timestamp}</td>"
                f"<td>{_format_interval(interval)}</td>"
                "</tr>",
            )
    else:
        detail_rows.append(
            "<tr><td class=\"stats-message\" colspan=\"4\">该命令尚无调用记录。</td></tr>",
        )

    return await _render_image(
        application_name = f"命令统计 · {escaped_key} · 累计 {total} 次",
        table_head = command_detail_head,
        table_body = "\n".join(detail_rows),
        footer = f"近 30 日趋势与最近 20 次调用 · 更新于 {now:%Y-%m-%d %H:%M:%S}",
    )

async def render_command_statistics(command_query: str = "") -> MessageSegment:
    now = datetime.now()
    available_keys = _available_command_keys()
    query = command_query.strip()
    if not query:
        return await _render_overview(available_keys, now)
    command_key = _resolve_command_key(query, available_keys)
    if command_key is None:
        return await _render_unknown_command(query, available_keys, now)
    return await _render_detail(command_key, now)
