import json
from functools import lru_cache

from src.const.jx3.kungfu import Kungfu
from src.const.path import ASSETS, build_path


FORMULATION_PATH = build_path(ASSETS, ["source", "jx3", "kungfu_formulations.json"])
SKILL_PATH = build_path(ASSETS, ["source", "jx3", "tabs", "Skill.txt"])
LEVEL_NAMES = {
    1: "一重",
    2: "二重",
    3: "三重",
    4: "四重",
    5: "五重",
    6: "六重",
    7: "闭阵",
}


@lru_cache(maxsize=1)
def _load_formulations() -> dict[str, int]:
    with open(FORMULATION_PATH, encoding="utf-8") as formulation_file:
        return json.load(formulation_file)


@lru_cache(maxsize=1)
def _load_skill_rows() -> list[dict[str, str]]:
    with open(SKILL_PATH, encoding="gbk") as skill_file:
        rows = [line.rstrip("\n").split("\t") for line in skill_file]
    headers = rows[0]
    return [dict(zip(headers, row)) for row in rows[1:]]


def _format_desc(desc: str) -> str:
    return desc.replace("\\n", "\n").strip()


def _get_formulation_skill(skill_id: int) -> tuple[str, list[str]] | None:
    skill_rows = [
        row
        for row in _load_skill_rows()
        if row.get("SkillID") == str(skill_id)
    ]
    if not skill_rows:
        return None

    skill_rows.sort(key=lambda row: int(row.get("Level") or 0))
    skill_name = skill_rows[0].get("Name") or "阵眼"
    descriptions = []
    for row in skill_rows:
        desc = _format_desc(row.get("Desc", ""))
        if not desc:
            continue
        level = int(row.get("Level") or 0)
        level_name = LEVEL_NAMES.get(level, f"{level}重")
        descriptions.append(f"{level_name}：{desc}")
    return skill_name, descriptions


async def get_matrix(kungfu: Kungfu):
    if kungfu.name is None or kungfu.id is None:
        return "此心法不存在哦，请检查后重试。"

    pc_kungfu = Kungfu.with_internel_id(kungfu.id, convert_to_pc=True)
    if pc_kungfu.name is None or pc_kungfu.id is None:
        return "阵眼查询仅支持 PC 心法，请检查后重试。"

    formulation_skill_id = _load_formulations().get(str(pc_kungfu.id))
    if formulation_skill_id is None:
        return f"暂时未找到{pc_kungfu.name}的阵眼数据，请稍后重试。"

    formulation_skill = _get_formulation_skill(formulation_skill_id)
    if formulation_skill is None:
        return f"查到了{pc_kungfu.name}的阵眼技能 ID：{formulation_skill_id}，但 Skill.txt 中没有对应数据。"

    skill_name, descriptions = formulation_skill
    if not descriptions:
        return f"查到了{pc_kungfu.name}的{skill_name}，但暂时没有阵眼效果数据。"
    return f"查到了{pc_kungfu.name}的{skill_name}：\n" + "\n".join(descriptions)
