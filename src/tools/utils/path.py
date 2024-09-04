import os
from pathlib import Path

tools_path = f"{os.getcwd()}/src/tools"

def get_path(path: str) -> str:
    t = Path(tools_path)
    return str(t.parent.joinpath(path))

DATA = get_path("data")
CACHE = get_path("cache")
ASSETS = get_path("assets")
CLOCK = get_path("clock")
VIEWS = get_path("views")
PLUGINS = get_path("plugins")
CONSTANT = get_path("constant")
TOOLS = tools_path