from pathlib import Path
from typing import List
import os

UTILS: str = f"{os.getcwd()}/src/utils"

def get_path(path: str) -> str:
    t = Path(UTILS)
    return str(t.parent / path).replace("\\", "/")

DATA: str = get_path("data")
CACHE: str = get_path("cache")
ASSETS: str = get_path("assets")
TEMPLATES: str = get_path("templates")
PLUGINS: str = get_path("plugins")
CONST: str = get_path("const")
CONFIG: str = get_path("config")

def build_path(const: str, path: List[str], end_with_slash: bool = False) -> str:
    end = "" if not end_with_slash else "/"
    return (os.path.join(const, *path) + end).replace("\\", "/")