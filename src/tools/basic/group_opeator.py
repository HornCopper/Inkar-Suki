from ..basic import DATA, read, write

import json

def getGroupData(group: str, key: str):
    data = json.loads(read(DATA + "/" + str(group) + "/settings.json"))
    if not data:
        return False
    return data[key]

def setGroupData(group: str, key: str, new):
    data = json.loads(read(DATA + "/" + str(group) + "/settings.json"))
    if not data:
        return False
    data[key] = new
    write(DATA + "/" + str(group) + "/settings.json", json.dumps(data, ensure_ascii=False))
    return True