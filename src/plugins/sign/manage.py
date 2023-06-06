from src.tools.file import read, write
import random
import json
import sys
import nonebot

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
CLOCK = TOOLS[:-5] + "clock"


class SignInRecord:
    def init_lucky(self, luck: int = None):
        if not luck:
            luck = random.randint(0, 10000)
        if luck < 1000:
            return 0
        elif luck < 7500:
            return 1
        elif luck < 9000:
            return 2
        return 3

    def __init__(self) -> None:
        self.user_id: str = None
        self.continuous: int = 0
        self.coin: int = 0
        self.luck: int = self.init_lucky()
        self.msg:str = None


class Sign:

    def generate_everyday_reward(qq: str):
        signed_list = json.loads(read(CLOCK + "/signed.json")) or []
        rank = len(signed_list)

        s = SignInRecord()
        continious = Sign.get_continuity(qq)
        s.coin = random.randint(1, 100) * (s.luck + 1)
        lottery = random.randint(0, 100)
        wlottery = False
        if lottery % 10 == 0:
            s.coin += 100
            wlottery = True
            s.wlottery = 1
        luck_desc = ['末吉签', '中吉签', '上吉签', '上上签'][s.luck]
        luck_desc = f'{luck_desc}(x{s.luck+1})'
        msg = f'\n签到成功！\n金币：+{s.coin}\n今日运势：{s.luck}'
        if wlottery:
            msg = f"{msg}\n触发额外奖励！已帮你额外添加了100枚金币！"
        msg = f"{msg}\n已连续签到{continious}天！"
        msg = f"{msg}\n您是第{rank+1}位签到的哦~"
        s.msg = msg
        return s

    def wsigned(qq: int):
        signed = json.loads(read(CLOCK + "/signed.json")) or []
        if str(qq) in signed:
            return True
        return False

    def save_data(data:SignInRecord, qq):
        qq = str(qq)
        signed_list = json.loads(read(CLOCK + "/signed.json")) or []
        signed_list.append(qq)
        write(CLOCK + "/signed.json", json.dumps(signed_list, ensure_ascii=False))
        accounts = json.loads(read(CLOCK + "/account.json")) or []
        for i in accounts:
            if i["id"] == qq:
                nc = i["coin"]
                fc = nc + data.coin
                i["coin"] = fc
                nt = i["continuity"]
                ft = nt + 1
                i["continuity"] = ft
                write(CLOCK + "/account.json",
                      json.dumps(accounts, ensure_ascii=False))
                return
        accounts.append(
            {
                "id": qq,
                "coin": 0 + data.coin,
                "continuity": 1
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
