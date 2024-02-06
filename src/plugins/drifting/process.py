from src.tools.dep import *

bottle_path = bot_path.CLOCK + "/bottles.json"

async def checkBottle(data: list, sender: str = None, msg: str = None, id: str = None, admin: bool = False):
    a1 = bool(msg) == bool(id)
    a2 = bool(msg) == bool(id)
    if a1 != a2:
        raise ValueError("The function `checkBottle` can only receive one argument from the `msg` and the `id`!")
    current = json.loads(read(bottle_path))
    for i in current:
        if id == None:
            if i["msg"] == msg and i["sender"] == sender:
                return i["id"]
        if msg == None:
            if admin:
                if i["id"] == id:
                    user = i["sender"]
                    user_msg = i["msg"]
                    final_msg = f"找到了来自「{user}」的漂流瓶：\n{user_msg}"
                    return final_msg
            else:
                if i["id"] == id and i["sender"] == sender:
                    return i["msg"]
    return False

async def createBottle(msg: str, sender: str, anonymous: bool):
    filter = await get_api(f"https://api.wer.plus/api/min?t={msg}")
    if filter["num"] != 0:
        return "唔……检测到违禁词了呢，请检查后重新投掷？"
    current = json.loads(read(bottle_path))
    status = await checkBottle(current, sender, msg)
    if status:
        return "投掷失败，我们已经发现了一个相同的瓶子，如果你需要删除，请发送：\n删除漂流瓶 " + status
    new_id = len(current) + 1
    new = {
        "id": new_id,
        "msg": msg,
        "sender": sender,
        "anonymous": anonymous
    }
    current.append(new)
    write(bottle_path, json.dumps(current, ensure_ascii=False))
    return [new_id]

async def deleteBottle(sender: str, id: str, admin: bool = False):
    current = json.loads(read(bottle_path))
    status = await checkBottle(current, sender, id=id, admin=admin)
    if not status:
        return "这个漂流瓶不是你投掷的或尚未被投，请检查后重试？"
    else:
        current = json.loads(read(bottle_path))
        for i in current:
            if i["id"] == id:
                if admin:
                    current.remove(i)
                    write(bottle_path, json.dumps(current, ensure_ascii=False))
                    return True
                else:
                    if i["sender"] == sender:
                        current.remove(i)
                        write(bottle_path, json.dumps(current, ensure_ascii=False))
                        return True

async def reportBottle(sender: str, id: str):
    current = json.loads(read(bottle_path))
    status = await checkBottle(current, sender, id=id)
    if status:
        return "请不要举报自己的漂流瓶。"
    status = await checkBottle(current, id=id)
    if status:
        return [id] # 返回ID的值，检测返回类型，如果是`str`则提交给机器人主人。
    else:
        return "这个漂流瓶不是你投掷的或尚未被投，请检查后重试？"   
    
async def lookupBottle(id: str):
    current = json.loads(read(bottle_path))
    status = await checkBottle(current, id=id, admin=True)
    return status if status else "没有找到这个漂流瓶哦~"

async def randomBottle():
    current = json.loads(read(bottle_path))
    rdnum = random.randint(0, len(current)-1)
    anonymous = current[rdnum]["anonymous"]
    msg = current[rdnum]["msg"]
    id = str(current[rdnum]["id"])
    sender = current[rdnum]["sender"] if not anonymous else "匿名"
    return f"这是一个来自「{sender}」的漂流瓶（ID为{id}）：\n{msg}"

def mapping(raw: str):
    if raw in ["匿名", "n", "匿", "腻了", "匿了", "N", "是", "1", "y", "Y"]:
        return True
    else:
        return False