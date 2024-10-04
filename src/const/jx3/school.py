from typing import List, Dict
from typing_extensions import Self

from src.utils.analyze import invert_dict
from src.const.path import (
    ASSETS,
    build_path
)
from src.const.jx3.kungfu import Kungfu, kungfu_colors_data

from .constant import school_aliases_data, school_internel_id_data

class School:
    school_aliases: Dict[str, List[str]] = school_aliases_data
    school_internel_id: Dict[str, str] = school_internel_id_data

    kungfu_colors: Dict[str, str] = kungfu_colors_data

    def __init__(self, school_name: str = ""):
        self.school_name = school_name

    @classmethod
    def with_internel_id(cls, internel_id: int | str) -> Self:
        if str(internel_id) not in cls.school_internel_id:
            return cls()
        return cls(cls.school_internel_id[str(internel_id)])
    
    @property
    def name(self) -> str | None:
        data = self.school_aliases
        for school_name in data:
            if self.school_name in data[school_name] or self.school_name == school_name:
                return school_name
        return None
    
    @property
    def internel_id(self) -> int | None:
        data = invert_dict(self.school_internel_id)
        if self.name in data:
            return int(data[self.name])
        return None
        
    @property
    def color(self) -> str:
        """
        门派颜色目前直接取门派下心法的颜色。
        """
        for kungfu, color in self.kungfu_colors.items():
            if Kungfu(kungfu).school == self.school_name:
                return color
        return "#FFFFFF"
    
    @property
    def icon(self) -> str:
        """
        门派图标。
        """
        if self.name is None:
            return ""
        return build_path(
            ASSETS,
            [
                "image",
                "jx3",
                "school",
                self.name + ".png"
            ]
        )