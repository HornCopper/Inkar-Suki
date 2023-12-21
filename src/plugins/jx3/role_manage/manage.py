from src.tools.dep import *

async def getPersonInfo(server: str, name: str, string: str = ""):
    url = f"https://www.jx3api.com/data/role/detailed?token={token}&server={server}&name={name}"
    data = await get_api(url)
    if data["code"] != 200:
        return False
    if data["data"]["personId"] in [None, ""]:
        return False
    data = data["data"]
    data["status"] = False
    data["verify"] = string
    return data

async def check_sign(personid, special_string: str = "", location: bool = False):
    param = {
        "personId": personid,
        "ts": gen_ts()
    }
    param = format_body(param)
    xsk = gen_xsk(param)
    headers = {
        "Host": "m.pvp.xoyo.com",
        "Accept": "application/json",
        "Accept-Language": "zh-cn",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "cache-control": "no-cache",
        "fromsys": "APP",
        "clientkey": "1",
        "apiversion": "3",
        "gamename": "jx3",
        "platform": "ios",
        "sign": "true",
        "token": token,
        "deviceid": device_id,
        "User-Agent": "SeasunGame/193 CFNetwork/1240.0.4 Darwin/20.6.0",
        "x-sk": xsk
    }
    data = await post_url("https://m.pvp.xoyo.com/user/home-page/basic", headers=headers, data=param)
    data = json.loads(data)
    if data["data"]["personInfo"]["signature"].find(special_string) != -1:
        if location:
            return data["data"]["personInfo"]["ipLocation"]
        else:
            return True
    return False

def init_folder():
    if os.path.exists(TOOLS + "/bindrole.json") == False:
        write(TOOLS + "/bindrole.json", "[]")

def readData():
    data = json.loads(read(TOOLS + "/bindrole.json"))
    return data

def checkWtrIn(server: str = "", name: str = "", user: str = ""):
    data = readData()
    for i in data:
        if i["user_id"] == user:
            for x in i["roles"]:
                if x["serverName"] == server and x["roleName"] == name:
                    return True
    return False

async def addRole(server: str = "", name: str = "", user: str = "", string: str = ""):
    if checkWtrIn(server, name, user):
        return 2 #已绑定
    role_data = await getPersonInfo(server, name, string)
    if role_data == False:
        return 0 #未找到角色
    data = readData()
    for i in data:
        if i["user_id"] == user:
            i["roles"].append(role_data)
            write(TOOLS + "/bindrole.json", json.dumps(data, ensure_ascii=False))
            return 1 #成功

def delRole(server: str, name: str, user: str):
    if checkWtrIn(server, name, user) == False:
        return 0 #未绑定
    data = readData()
    for i in data:
        if i["user_id"] == user:
            for x in i["roles"]:
                if x["serverName"] == server and x["roleName"] == name:
                    i["roles"].remove(x)
                    write(TOOLS + "/bindrole.json", json.dumps(data, ensure_ascii=False))
                    return 1 #成功

def passVerify(server: str, name: str, user: str):
    if checkWtrIn(server, name, user) == False:
        return 0 #未绑定
    data = readData()
    for i in data:
        if i["user_id"] == user:
            for x in i["roles"]:
                if x["serverName"] == server and x["roleName"] == name:
                    x["status"] = True
                    write(TOOLS + "/bindrole.json", json.dumps(data, ensure_ascii=False))
                    return 1 #成功
                
def checkVerify(server: str, name: str, user: str):
    if checkWtrIn(server, name, user) == False:
        return 0 #未绑定
    data = readData()
    for i in data:
        if i["user_id"] == user:
            for x in i["roles"]:
                if x["serverName"] == server and x["roleName"] == name:
                    return x["status"]
    return False

def getData(server: str, name: str, user: str):
    if checkWtrIn(server, name, user) == False:
        return 0 #未绑定
    data = readData()
    for i in data:
        if i["user_id"] == user:
            for x in i["roles"]:
                if x["serverName"] == server and x["roleName"] == name:
                    return x
    return False

def getRoleList(user):
    data = readData()
    role = []
    for i in data:
        if i["user_id"] == user:
            if len(i["roles"]) == 0:
                return 0
            for x in i["roles"]:
                role.append(x["serverName"] + "|" + x["roleName"] + "|" + "已验证" if x["status"] else "未验证")
            return role
    return -1

def getAllRole(user, verify, dtype):
    data = readData()
    role = []
    for i in data:
        if i["user_id"] == user:
            if len(i["roles"]) == 0:
                return 0
            for x in i["roles"]:
                if verify:
                    if x["status"]:
                        if dtype:
                            msg = [x["serverName"], x["roleName"], x["globalRoleId"]]
                        else:
                            msg = [x["serverName"], x["roleName"], x["roleId"]]
                        msg = "|".join(msg)
                        role.append(msg)
                    else:
                        pass
                else:
                    if dtype:
                        msg = [x["serverName"], x["roleName"], x["globalRoleId"]]
                    else:
                        msg = [x["serverName"], x["roleName"], x["roleId"]]
                    msg = "|".join(msg)
                    role.append(msg)
            return role if len(role) > 0 else 0
    return -1
    
def createRecord(user):
    new = {
        "user_id": user,
        "roles": []
    }
    data = readData()
    data.append(new)
    write(TOOLS + "/bindrole.json", json.dumps(data, ensure_ascii=False))

async def getRoleCd(guid):
    ts = gen_ts()
    param = {
        "globalRoleId": guid,
        "sign": dungeon_sign(f"globalRoleId={guid}&ts={ts}"),
        "ts": ts
    }
    param = format_body(param)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip",
        "Accept-Language": "zh-cn",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "m.pvp.xoyo.com",
        "Origin": "https://w.pvp.xoyo.com:31727",
        "User-Agent": "SeasunGame/178 CFNetwork/1240.0.2 Darwin/20.5.0",
        "token": ticket,
        "X-Sk": gen_xsk(param)
    }
    data = await post_url("https://m.pvp.xoyo.com/h5/parser/cd-process/get-by-role", headers=headers, data=param)
    return json.loads(data)["data"]

def searchData(mapName: str, data: dict):
    for i in data:
        if mapName == (i["mapType"] + i["mapName"]):
            status = []
            for x in i["bossProgress"]:
                status.append(x["finished"])
            return status
    return 0 # 没有打过