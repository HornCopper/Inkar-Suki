import pathlib2
from .bot import *
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)


def get_path(path: str) -> str:
    t = pathlib2.Path(TOOLS)
    return t.parent.joinpath(path).__str__()


DATA = get_path("data")
CACHE = get_path("cache")
ASSETS = get_path("assets")
