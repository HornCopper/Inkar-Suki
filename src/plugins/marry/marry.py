import json
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent.parent / "tools"


def already_married(obj):
    cache = open(TOOLS / "marry.json", mode="r")
    marrylist = json.loads(cache.read())
    cache.close()
    for i in marrylist:
        if i["wife"] == obj or i["husband"] == obj:
            return True
        else:
            continue
    return False