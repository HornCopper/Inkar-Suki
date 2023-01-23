import random
import json
import sys
import nonebot

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
CLOCK = TOOLS[:-5] + "clock"

from file import read, write

class Sign:
    def lucky_level(luck: int):
        if 0 <= luck < 2500:
            return 0
        elif 2500 <= luck < 5000:
            return 1
        elif 5000 <= luck < 7500:
            return 2
        elif 5000 <= luck < 10000:
            return 3
    def generate_everyday_reward():
        coin = random.randint(1,100)
        luck = Sign.lucky_level(random.randint(0,10000))
        coin = coin * (luck + 1)
        lottery = random.randint(0,100)
        wlottery = False
        if lottery % 10 == 0:
            coin = coin + 100
            wlottery = True
        signed_list = json.loads(read(CLOCK + "/signed.json"))
        signed_people = len(signed_list)
        data = {
            "coin": coin,
            "luck": luck,
            "wlottery": wlottery,
            "signed":signed_people
        }
        return data
    def wsigned(qq: int):
        signed = json.loads(read(CLOCK + "/signed.json"))
        if str(qq) in signed:
            return True
        return False
    def save_data(data, qq):
        qq = str(qq)
        signed_list = json.loads(read(CLOCK + "/signed.json"))
        signed_list.append(qq)
        write(CLOCK + "/signed.json", json.dumps(signed_list, ensure_ascii=False))
        accounts = json.loads(read(CLOCK + "/account.json"))
        for i in accounts:
            if i["id"] == qq:
                nc = i["coin"]
                fc = nc + data["coin"]
                i["coin"] = fc
                nt = i["continuity"]
                ft = nt + 1
                i["continuity"] = ft
                write(CLOCK + "/account.json", json.dumps(accounts, ensure_ascii=False))
                return
        accounts.append(
            {
                "id":qq,
                "coin": 0 + data["coin"],
                "continuity":1
            }
        )
        write(CLOCK + "/account.json", json.dumps(accounts, ensure_ascii=False))
        return
    def get_continuity(qq):
        qq = str(qq)
        accounts = json.loads(read(CLOCK + "/account.json"))
        for i in accounts:
            if i["id"] == qq:
                return i["continuity"]
        return False
    def get_coin(qq):
        qq = str(qq)
        accounts = json.loads(read(CLOCK + "/account.json"))
        for i in accounts:
            if i["id"] == qq:
                return i["coin"]
        return False