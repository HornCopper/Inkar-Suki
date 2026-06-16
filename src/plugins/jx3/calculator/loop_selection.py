from __future__ import annotations

from typing import Any, Protocol


CALCULATOR_CUSTOM_LOOP_ERROR = (
    "未找到可用的公有循环或自定义循环，请检查计算器循环库或上传自定义 JCL！\n"
    "切换方式：发送「偏好 计算器来源 公用」"
)
CALCULATOR_PUBLIC_LOOP_ERROR = (
    "该玩家下线时的心法当前尚未实现计算器，可尝试使用指定计算器（如有）或等待该心法支持！\n"
    "也可能是当前使用的计算器循环库中并无该心法，请切换公用循环库或自定义循环库，详情见「偏好」。"
)


class CalculatorLoopProvider(Protocol):
    async def get_loop(self, user_id: int = 0) -> dict[str, dict[str, str]] | str:
        ...


def calculator_loop_entries_from_map(
    loops: dict[str, dict[str, str]],
    section: str,
    user_id: int,
) -> list[dict[str, Any]]:
    return [
        {
            "display_name": loop_name,
            "section": section,
            "user_id": user_id,
            **loop_data,
        }
        for loop_name, loop_data in loops.items()
    ]


async def calculator_loop_entries(
    instance: CalculatorLoopProvider,
    user_id: int,
    is_custom: bool,
    *,
    public_error: str = CALCULATOR_PUBLIC_LOOP_ERROR,
    custom_error: str = CALCULATOR_CUSTOM_LOOP_ERROR,
) -> list[dict[str, Any]] | str:
    if is_custom:
        public_loops = await instance.get_loop(0)
        custom_loops = await instance.get_loop(user_id)
        loop_entries: list[dict[str, Any]] = []
        if not isinstance(public_loops, str):
            loop_entries.extend(calculator_loop_entries_from_map(public_loops, "公有循环", 0))
        if not isinstance(custom_loops, str):
            loop_entries.extend(calculator_loop_entries_from_map(custom_loops, "自定义循环", user_id))
        return loop_entries or custom_error

    loops = await instance.get_loop(0)
    if isinstance(loops, str):
        return public_error
    return calculator_loop_entries_from_map(loops, "", 0)


def format_calculator_loop_selection(entries: list[dict[str, Any]], prompt: str = "请选择计算循环！") -> str:
    msg = prompt
    current_section = ""
    for index, entry in enumerate(entries, start=1):
        section = str(entry.get("section") or "")
        if section and section != current_section:
            msg += f"\n【{section}】"
            current_section = section
        msg += f"\n{index}. {entry.get('display_name') or '未命名循环'}"
    return msg
