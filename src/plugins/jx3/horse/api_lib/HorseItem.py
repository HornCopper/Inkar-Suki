from src.tools.dep import *


class HorseItem:
    MAX_Preserve_Days: int = 30
    id: str
    timestamp: DateTime

    @property
    def outdated(self):
        return (DateTime() - self.timestamp).days > HorseItem.MAX_Preserve_Days


class HorseInfo(StaticLoader):
    resource_url: str = pathlib2.Path(__file__).parent.joinpath("config.horse.static.json").as_posix()
    resource_type: str = "file"
    icon_url: str = "https://img.jx3box.com/horse/std/"

    def __init__(self, key: str, data: dict) -> None:
        self.key = key
        self.id = data.get("id")
        self.item_id = data.get("itemId")

    @property
    def icon(self):
        return f"{HorseInfo.icon_url}{self.id}.png"

    @classmethod
    def from_id(cls, name: str):
        return super().from_id(name)

    def to_dict(self):
        return {
            "name": self.key,
            "id": self.id,
            "item_id": self.item_id,
        }
