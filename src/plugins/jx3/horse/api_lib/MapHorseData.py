from .MapData import *


class MapHorseData(StaticLoader):
    # TODO 剑三盒子使用了硬编码，应从其文件中获取
    resource_url: str = pathlib2.Path(__file__).parent.joinpath(
        "config.map_horse.static.json").as_posix()
    resource_type: str = "file"

    def __init__(self, key: str, data: dict) -> None:
        self.key = key
        self.data = data
        self.coordinates: list[dict] = data.get("coordinates")  # {x:0,y:0,z:0}
        self.name = data.get("mapName")
        self.horse: list[str] = data.get("horse")

    def to_dict(self):
        return {
            "name": self.key,
            "coordinates": self.coordinates
        }


class MapDataWithHorse(MapHorseData, MapData):
    def __init__(self, horse: MapHorseData, map: MapData) -> None:
        if not isinstance(horse, MapHorseData):
            raise InvalidArgumentException("hourse->MapHorseData")
        if not isinstance(map, MapData):
            raise InvalidArgumentException("map->MapData")
        self.map_id = map.map_id
        self.map_name = map.map_name
        self.points = map.points

        self.coordinates = horse.coordinates
        self.horses = horse.horse

    def to_dict(self):
        return {
            "map_id": self.map_id,
            "map_name": self.map_name,
            "points": [self.points[x].to_dict() for x in self.points], # TODO 多态继承

            "coordinates": self.coordinates,
            "horses": self.horses,
        }
