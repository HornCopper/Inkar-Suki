import pathlib2
import sys
import nonebot
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)


def get_path(path: str) -> str:
    t = pathlib2.Path(TOOLS)
    return t.parent.joinpath(path).__str__()


DATA = get_path("data")
CACHE = get_path("cache")
ASSETS = get_path("assets")
CLOCK = get_path("clock")
VIEWS = get_path("views")
PLUGINS = get_path('plugins')
