"""展开技能与当前奇穴描述中的术语、奇穴条件及技能引用。"""

from collections import deque
from functools import lru_cache
import json
import re

from src.utils.jx3_tables import rows


NOUN_PATTERN = re.compile(r"<NounID\s+(\d+)\s*>")
NOUN_REFERENCE_PATTERN = re.compile(
    r"<NounID\s+(?P<noun_id>\d+)\s*>|"
    r"<SUB_NOUN\s+(?P<skill_id>\d+)\s+(?P<level>\d+)\s+(?P<label>[^<>]+)>"
)
TALENT_START_PATTERN = re.compile(r"<TALENT\s+(\d+)\s+(\d+)(?:\s+|(?=>))")
TALENT_CORE_PATTERN = re.compile(r"<TALENT_CORE\s+(\d+)\s+(\d+)\s*>")
_ESCAPE_PATTERN = re.compile(r'\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4})')


@lru_cache(maxsize = 1)
def load_skill_nouns() -> dict[int, tuple[str, str]]:
    return {
        int(row["nNounID"]): (row["szName"], row.get("szDesc", ""))
        for row in rows("skill/Skill_Nouns.txt") if row["nNounID"].isdigit() and row.get("szName")
    }


@lru_cache(maxsize = 1)
def load_skill_descriptions() -> dict[tuple[int, int], tuple[str, str]]:
    descriptions = {}
    for row in rows("skill/Skill.txt"):
        if row["SkillID"].isdigit() and row["Level"].isdigit() and row.get("Name"):
            descriptions.setdefault((int(row["SkillID"]), int(row["Level"])),
                                    (row["Name"], row.get("Desc", "")))
    return descriptions


@lru_cache(maxsize = 1)
def load_skill_names() -> dict[tuple[int, int], str]:
    return {key: value[0] for key, value in load_skill_descriptions().items()}


@lru_cache(maxsize = 1)
def load_skill_icons() -> dict[tuple[int, int], str]:
    return {
        (int(row["SkillID"]), int(row["Level"])): row["IconID"]
        for row in rows("skill/Skill.txt")
        if row["SkillID"].isdigit() and row["Level"].isdigit() and row.get("IconID")
    }


def _skill_description(skill_id: int, level: int) -> tuple[str, str] | None:
    descriptions = load_skill_descriptions()
    return descriptions.get((skill_id, level)) or descriptions.get((skill_id, 0)) or descriptions.get((skill_id, 1))


def expand_skill_talents(description: str, _path: tuple[tuple[int, int], ...] = (), *,
                         talent_references: list[tuple[int, int, str]] | None = None) -> str:
    if "<TALENT" not in description:
        return description
    parts = []
    sections = []
    offset = 0
    while match := TALENT_START_PATTERN.search(description, offset):
        # 条件效果中也可能有 SUB、BUFF 等标签，需找到外层 TALENT 的结束位置。
        depth = 1
        end = match.end()
        while end < len(description):
            if description[end] == "<":
                depth += 1
            elif description[end] == ">":
                depth -= 1
                if depth == 0:
                    break
            end += 1
        if depth:
            break
        parts.append(description[offset:match.start()])
        key = (int(match[1]), int(match[2]))
        entry = _skill_description(*key)
        if entry is None or key in _path or len(_path) >= 20:
            parts.append(description[match.start():end + 1])
        else:
            name, original = entry
            if talent_references is not None:
                talent_references.append((*key, name))
            content = description[match.end():end].strip()
            detail = original if not content or content == name else content
            detail = expand_skill_talents(detail, (*_path, key), talent_references = talent_references)
            sections.append(f"【奇穴 {name}】{detail}")
        offset = end + 1
    if not sections:
        return description
    parts.append(description[offset:])
    return "\n".join(part for part in ("".join(parts).rstrip("\n"), *sections) if part)


def expand_skill_nouns(description: str, nouns: dict[int, tuple[str, str]] | None = None, *,
                       talent_references: list[tuple[int, int, str]] | None = None) -> str:
    if "<NounID" not in description and "<SUB_NOUN" not in description:
        return description
    nouns = load_skill_nouns() if nouns is None else nouns
    pending: deque[tuple[str, str]] = deque()
    seen: set[int] = set()
    seen_skills: set[tuple[int, int, str]] = set()

    def replace(match: re.Match[str]) -> str:
        if match["skill_id"] is not None:
            skill_id, level = int(match["skill_id"]), int(match["level"])
            entry = _skill_description(skill_id, level)
            if entry is None:
                return match[0]
            label = match["label"].strip()
            key = (skill_id, level, label)
            if key not in seen_skills:
                seen_skills.add(key)
                pending.append((label, entry[1]))
            return f"[{label}]"
        noun_id = int(match["noun_id"])
        noun = nouns.get(noun_id)
        if noun is None:
            return match[0]
        if noun_id not in seen:
            seen.add(noun_id)
            pending.append(noun)
        return f"[{noun[0]}]"

    parts = [NOUN_REFERENCE_PATTERN.sub(replace, description)]
    while pending:
        name, detail = pending.popleft()
        if detail:
            detail = expand_skill_talents(detail, talent_references = talent_references)
            parts.append(f"[{name}]：{NOUN_REFERENCE_PATTERN.sub(replace, detail)}")
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


def format_skill_description(description: str, *,
                              talent_references: list[tuple[int, int, str]] | None = None) -> str:
    expanded = expand_skill_talents(description, talent_references = talent_references)
    expanded = expand_skill_talent_cores(expand_skill_nouns(expanded, talent_references = talent_references))
    # 接口的 DisplayDesc 可以已有实际换行；只解码合法转义，保留引号及未知标记。
    decoded = _ESCAPE_PATTERN.sub(lambda match: json.loads('"' + match[0] + '"'), expanded)
    return re.sub(r"<br\s*/?>", "\n", decoded, flags = re.IGNORECASE)
