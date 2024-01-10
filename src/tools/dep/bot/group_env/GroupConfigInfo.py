from __future__ import annotations


class GroupConfigInfo:
    name: str
    description: str
    default: any
    infos: dict[str, GroupConfigInfo]

    def __init__(self, name: str, description: str = None, default: any = None, infos: dict[str, GroupConfigInfo] = None) -> None:
        self.name = name
        self.description = description
        self.default = default
        self.infos = infos
