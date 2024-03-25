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
TOOLS = tools_path

common_data: str = "common"
common_data_full: str = f"{DATA}/{common_data}/"
"""DATA中的数据通用存储"""