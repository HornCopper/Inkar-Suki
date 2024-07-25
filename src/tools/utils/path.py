import os
import pathlib2

tools_path = f"{os.getcwd()}/src/tools"

def get_path(path: str) -> str:
    t = pathlib2.Path(tools_path)
    return t.parent.joinpath(path).__str__()

DATA = get_path("data")
CACHE = get_path("cache")
ASSETS = get_path("assets")
CLOCK = get_path("clock")
VIEWS = get_path("views")
PLUGINS = get_path("plugins")
CONSTANT = get_path("constant")
TOOLS = tools_path