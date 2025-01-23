from typing_extensions import Self
from src.utils.analyze import invert_dict
from src.const.path import ASSETS, build_path

from .constant import (
    kungfu_aliases_data,
    kungfu_colors_data,
    kungfu_internel_id_data,
    kungfu_basic_data,
    kungfu_coefficient_data,
    kungfu_baseattr_data,
    school_aliases_data,
    school_snacks_data,
)


class Kungfu:
    kungfu_aliases: dict[str, list[str]] = kungfu_aliases_data
    kungfu_colors_data: dict[str, str] = kungfu_colors_data
    kungfu_internel_id: dict[str, str] = kungfu_internel_id_data
    kungfu_baseattr: dict[str, list[str]] = kungfu_baseattr_data
    kungfu_snacks: dict[str, list[str]] = school_snacks_data
    kungfu_basic: dict[str, dict] = kungfu_basic_data
    kungfu_coefficient: dict[str, list[float]] = kungfu_coefficient_data

    school_aliases: dict[str, list[str]] = school_aliases_data

    def __init__(self, kungfu_name: str | None = ""):
        self.kungfu_name = kungfu_name

    @classmethod
    def with_internel_id(cls, internel_id: int | str) -> Self:
        if str(internel_id) in invert_dict(cls.kungfu_internel_id):
            return cls(invert_dict(cls.kungfu_internel_id)[str(internel_id)])
        return cls()

    @property
    def name(self) -> str | None:
        """
        心法实际名称。
        """
        name = self.kungfu_name
        if name is None:
            return None
        if name.endswith("·悟"):
            return name
        for kungfu_name, aliases in self.kungfu_aliases.items():
            if name == kungfu_name or name in aliases:
                return kungfu_name
        return None

    @property
    def school(self) -> str | None:
        """
        所属门派。
        """
        name = self.name
        if name is None:
            return None
        if name == "山居问水剑·悟":
            name = "问水诀"
        if name.endswith("·悟"):
            name = name[:-2]
        for school_name, aliases in self.school_aliases.items():
            if name in aliases:
                return school_name
        return None

    @property
    def color(self) -> str:
        """
        心法颜色。
        """
        if self.name is None:
            return "#FFFFFF"
        if self.name == "山居问水剑·悟":
            return self.kungfu_colors_data.get("问水诀", "#FFFFFF")
        if self.name.endswith("·悟"):
            return self.kungfu_colors_data.get(self.name[:-2], "#FFFFFF")
        return self.kungfu_colors_data.get(self.name, "#FFFFFF")

    @property
    def icon(self) -> str:
        """
        心法图标。
        """
        if self.name is None:
            return (
                build_path(ASSETS, ["image", "jx3", "kungfu"], end_with_slash=True)
                + "通用.png"
            )
        return (
            build_path(ASSETS, ["image", "jx3", "kungfu"], end_with_slash=True)
            + self.name
            + ".png"
        )

    @property
    def base(self) -> str | None:
        """
        心法基础属性。

        防御与治疗不参与。
        """
        name = self.name
        if name is None:
            return
        if name == "山居问水剑·悟":
            name = "问水诀"
        if name.endswith("·悟"):
            name = name[:-2]
        for base_attr, kungfus in self.kungfu_baseattr.items():
            if name in kungfus:
                return base_attr
        return None

    @property
    def id(self) -> int | None:
        """
        心法ID。
        """
        if self.name is None:
            return None
        for kungfu in self.kungfu_internel_id:
            if kungfu == self.name:
                return int(self.kungfu_internel_id[kungfu])

    @property
    def snack(self):
        if self.name is None:
            return None
        name = self.name
        if name == "山居问水剑·悟":
            name = "问水诀"
        if name.endswith("·悟"):
            name = name[:-2]
        return self.kungfu_snacks[self.name]

    @property
    def abbr(self) -> str:
        if self.base not in ["治疗", "防御"]:
            return "D"
        elif self.base == "防御":
            return "T"
        else:
            return "N"
