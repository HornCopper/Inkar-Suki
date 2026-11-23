"""展开技能与当前奇穴描述中的术语和核心奇穴引用。"""

from collections import deque
from functools import lru_cache
import json
import re

from src.utils.jx3_tables import rows


NOUN_PATTERN = re.compile(r"<NounID\s+(\d+)\s*>")
TALENT_CORE_PATTERN = re.compile(r"<TALENT_CORE\s+(\d+)\s+(\d+)\s*>")
_ESCAPE_PATTERN = re.compile(r'\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4})')


@lru_cache(maxsize = 1)
def load_skill_nouns() -> dict[int, tuple[str, str]]:
    return {
        int(row["nNounID"]): (row["szName"], row.get("szDesc", ""))
        for row in rows("skill/Skill_Nouns.txt") if row["nNounID"].isdigit() and row.get("szName")
    }


@lru_cache(maxsize = 1)
def load_skill_names() -> dict[tuple[int, int], str]:
    names = {}
    for row in rows("skill/Skill.txt"):
        if row["SkillID"].isdigit() and row["Level"].isdigit() and row.get("Name"):
            names.setdefault((int(row["SkillID"]), int(row["Level"])), row["Name"])
    return names


def expand_skill_nouns(description: str, nouns: dict[int, tuple[str, str]] | None = None) -> str:
    if "<NounID" not in description:
        return description
    nouns = load_skill_nouns() if nouns is None else nouns
    pending: deque[int] = deque()
    seen: set[int] = set()

    def replace(match: re.Match[str]) -> str:
        noun_id = int(match[1])
        noun = nouns.get(noun_id)
        if noun is None:
            return match[0]
        if noun_id not in seen:
            seen.add(noun_id)
            pending.append(noun_id)
        return f"[{noun[0]}]"

    parts = [NOUN_PATTERN.sub(replace, description)]
    while pending:
        name, detail = nouns[pending.popleft()]
        if detail:
            parts.append(f"[{name}]：{NOUN_PATTERN.sub(replace, detail)}")
    return "\n".join(parts)


def expand_skill_talent_cores(description: str) -> str:
    if "<TALENT_CORE" not in description:
        return description
    names = load_skill_names()

    def replace(match: re.Match[str]) -> str:
        skill_id, level = map(int, match.groups())
        name = names.get((skill_id, level)) or names.get((skill_id, 0))
        return f"【需求核心奇穴 {name}】" if name else match[0]

    return TALENT_CORE_PATTERN.sub(replace, description)


def format_skill_description(description: str) -> str:
    expanded = expand_skill_talent_cores(expand_skill_nouns(description))
    # 接口的 DisplayDesc 可以已有实际换行；只解码合法转义，保留引号及未知标记。
    decoded = _ESCAPE_PATTERN.sub(lambda match: json.loads('"' + match[0] + '"'), expanded)
    return re.sub(r"<br\s*/?>", "\n", decoded, flags = re.IGNORECASE)
