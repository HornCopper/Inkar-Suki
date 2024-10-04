from src.utils.network import Request

async def get_preposition(name: str = ""):
    url = "https://inkar-suki.codethink.cn/serendipity"
    data = (await Request(url).get()).json()
    flag = False
    for i in data:
        if i["name"] == name:
            id = i["id"]
            flag = True
    if not flag:
        return False
    final_url = "https://jx3box.com/adventure/" + str(id)
    return f"【{name}】魔盒攻略：\n{final_url}"