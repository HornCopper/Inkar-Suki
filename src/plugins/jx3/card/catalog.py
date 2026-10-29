"""Portable, source-backed social-card materials; no bot or network imports."""
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import re

ASSETS = Path(__file__).resolve().parents[3] / "assets"
CATEGORIES = {
    "背景": "backgrounds",
    "背景皮肤": "backgrounds",
    "名片背景皮肤": "backgrounds",
    "头像": "avatars",
    "小头像": "avatars",
    "人物小头像": "avatars",
    "头像框": "frames",
    "银色头像框": "frames",
    "框": "frames",
}
LABELS = {"backgrounds": "背景", "avatars": "头像", "frames": "头像框"}
BODIES = {"f1": "萝莉", "f2": "成女", "m1": "正太", "m2": "成男"}
BODY_ALIASES = {
    **{
        key: key
        for key in BODIES
    },
    **{
        value: key
        for key, value in BODIES.items()
    },
    "少女": "f1",
    "少年": "m1",
}
PAGE_SIZE = 12

def normalized(value: str) -> str:
    return re.sub(r"[\s·・•]", "", value).casefold()

@dataclass(frozen = True)
class Selection:
    entry: dict
    body: str | None = None

class Catalog:

    def __init__(self, assets: Path = ASSETS):
        self.assets = Path(assets)
        self.root = self.assets / "image/jx3/card"
        self.data = json.loads((self.assets / "source/jx3/card/catalog.json").read_text(encoding = "utf-8"))

    def entries(self, category: str) -> list[dict]:
        return self.data[category]

    def path(self, reference: str) -> Path:
        # References only come from the bundled manifest, never command input.
        target = (self.root / reference).resolve()
        if not target.is_relative_to(self.root.resolve()):
            raise ValueError("素材清单路径无效。")
        return target

    @staticmethod
    def names(entry: dict) -> list[str]:
        return [entry["id"], entry["name"], *entry.get("names", []), *entry.get("aliases", [])]

    def search(self, category: str, keyword: str = "", body: str | None = None) -> list[dict]:
        words = [normalized(word) for word in keyword.split() if normalized(word)]
        return [
            entry for entry in self.entries(category) if (not body or body in entry.get("variants", {}))
            and all(any(word in normalized(name) for name in self.names(entry)) for word in words)
        ]

    def resolve(self, category: str, value: str) -> Selection:
        if category == "avatars":
            suffix = re.fullmatch(r"(.+)-(f1|f2|m1|m2|萝莉|成女|正太|成男)", value, re.IGNORECASE)
            if suffix:
                raise ValueError(f"头像体型由角色详情自动选择，请只填写头像编号或名称，如 {suffix[1]}。")
        needle = normalized(value)
        exact = [
            entry for entry in self.entries(category) if any(needle == normalized(name) for name in self.names(entry))
        ]
        matches = exact if value.isdecimal() else exact or self.search(category, value)
        label = LABELS[category]
        if not matches or not needle:
            raise ValueError(f"没有找到{label}「{value}」。发送“社交名片 {label}”查看可选图鉴。")
        if len(matches) != 1:
            examples = "、".join(f'{item["id"]} {item["name"]}' for item in matches[:6])
            raise ValueError(
                f"{label}「{value}」匹配到 {len(matches)} 项：{examples}。\n"
                f"请填编号或完整名称；发送“社交名片 {label} {value}”可看图。",
            )
        entry = matches[0]
        return Selection(entry)

    def variant(self, selection: Selection, role_body: str = "") -> dict:
        variants = selection.entry["variants"]
        body = BODY_ALIASES.get(role_body.casefold())
        if not body:
            raise ValueError("角色详情未提供可识别的体型，暂时无法生成名片，请稍后重试。")
        if body not in variants:
            raise ValueError(f"该头像没有{BODIES[body]}版本，请在“社交名片 头像”中重新选择。")
        return variants[body]

@lru_cache(maxsize = 1)
def get_catalog() -> Catalog:
    return Catalog()
