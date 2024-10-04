from src.const.path import (
    ASSETS,
    build_path
)

import json

with open(build_path(ASSETS, ["source", "jx3", "dungeon_name.json"]), encoding="utf-8", mode="r") as dungeon_name:
    dungeon_name_data = json.loads(dungeon_name.read())

with open(build_path(ASSETS, ["source", "jx3", "dungeon_mode.json"]), encoding="utf-8", mode="r") as dungeon_mode:
    dungeon_mode_data = json.loads(dungeon_mode.read())

with open(build_path(ASSETS, ["source", "jx3", "kungfu_aliases.json"]), encoding="utf-8", mode="r") as kungfu_aliases:
    kungfu_aliases_data = json.loads(kungfu_aliases.read())

with open(build_path(ASSETS, ["source", "jx3", "kungfu_colors.json"]), encoding="utf-8", mode="r") as kungfu_colors:
    kungfu_colors_data = json.loads(kungfu_colors.read())

with open(build_path(ASSETS, ["source", "jx3", "kungfu_internel_id.json"]), encoding="utf-8", mode="r") as kungfu_internel_id:
    kungfu_internel_id_data = json.loads(kungfu_internel_id.read())

with open(build_path(ASSETS, ["source", "jx3", "kungfu_baseattr.json"]), encoding="utf-8", mode="r") as kungfu_baseattr:
    kungfu_baseattr_data = json.loads(kungfu_baseattr.read())

with open(build_path(ASSETS, ["source", "jx3", "school_aliases.json"]), encoding="utf-8", mode="r") as school_aliases:
    school_aliases_data = json.loads(school_aliases.read())

with open(build_path(ASSETS, ["source", "jx3", "school_internel_id.json"]), encoding="utf-8", mode="r") as school_internel_id:
    school_internel_id_data = json.loads(school_internel_id.read())

with open(build_path(ASSETS, ["source", "jx3", "server_aliases.json"]), encoding="utf-8", mode="r") as server_aliases:
    server_aliases_data = json.loads(server_aliases.read())

with open(build_path(ASSETS, ["source", "jx3", "server_zones_mapping.json"]), encoding="utf-8", mode="r") as server_zones_mapping:
    server_zones_mapping_data = json.loads(server_zones_mapping.read())