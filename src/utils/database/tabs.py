from functools import lru_cache


@lru_cache(maxsize=None)
def read_tab(tab_path: str) -> list[list]:
    with open(tab_path, encoding="gbk", mode="r") as f:
        return [a.strip().split("\t") for a in f.read().strip().split("\n")]
