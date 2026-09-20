from src.const.path import ASSETS, build_path
from src.utils.database.tabs import read_tab


ADVENTURE_TABLE = build_path(
    ASSETS, ["source", "jx3", "tabs", "adventure", "Adventure.txt"]
)


async def get_preposition(name: str = ""):
    table = read_tab(ADVENTURE_TABLE)
    adventure_id = None
    for values in table[1:]:
        row = dict(zip(table[0], values))
        if name and row.get("szName") == name:
            adventure_id = row.get("dwID")
    if not adventure_id:
        return False
    final_url = f"https://jx3box.com/adventure/{adventure_id}"
    return f"【{name}】魔盒攻略：\n{final_url}"
