from functools import lru_cache
from io import StringIO
from pathlib import Path
from typing import Any, Iterator, cast

import csv

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "assets/source/jx3"
TABLE_ROOT = SOURCE_ROOT / "tabs"
TALENT_HISTORY_ROOT = SOURCE_ROOT / "talents/history"

def source_path(relative: str) -> Path:
    return TABLE_ROOT / relative

def integer(value: Any, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default

def rows(relative: str) -> Iterator[dict[str, str]]:
    """按客户端原始编码读取制表符分隔的表格。"""
    text = source_path(relative).read_bytes().decode("gb18030")
    reader = csv.DictReader(StringIO(text, newline = ""), delimiter = "\t")
    yield from cast(Iterator[dict[str, str]], reader)

@lru_cache(maxsize = None)
def table(relative: str, key: str = "ID", columns: tuple[str, ...] | None = None) -> dict[str, dict[str, str]]:
    """按指定字段建立索引，可仅缓存所需列。"""
    return {
        row[key]: {
            column: row.get(column, "")
            for column in columns
        } if columns else row
        for row in rows(relative) if row.get(key)
    }
