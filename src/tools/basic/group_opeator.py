from ..basic import DATA, read, write

import json

def getGroupData(group: str, key: str):
    data = json.loads(read(DATA + "/" + str(group) + "/jx3group.json"))
    if data == False:
        return False
    return data[key]

def setGroupData(group: str, key: str, new):
    data = json.loads(read(DATA + "/" + str(group) + "/jx3group.json"))
    if data == False:
        return False
    data[key] = new
    write(DATA + "/" + str(group) + "/jx3group.json", json.dumps(data, ensure_ascii=False))
    return True