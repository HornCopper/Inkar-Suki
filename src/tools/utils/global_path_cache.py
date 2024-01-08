import os
import pathlib2
import sys
tools_path = f"{os.getcwd()}/src/tools"
sys.path.append(tools_path)


def get_path(path: str) -> str:
    t = pathlib2.Path(tools_path)
    return t.parent.joinpath(path).__str__()


DATA = get_path("data")
CACHE = get_path("cache")
ASSETS = get_path("assets")
CLOCK = get_path("clock")
VIEWS = get_path("views")
PLUGINS = get_path('plugins')
TOOLS = tools_path

common_data: str = 'common'
common_data_full: str = f'{DATA}{os.sep}{common_data}{os.sep}'
'''DATA中的数据通用存储'''


def get_group_config(group_id: str, config_name: str = 'jx3group') -> str:
    return f'{DATA}{os.sep}{group_id}{os.sep}{config_name}'
