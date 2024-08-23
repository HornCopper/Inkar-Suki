from typing import Union

from src.constant.jx3 import school_name_aliases, force_list, kungfu_to_school

from src.tools.config import Config
from src.tools.utils.request import post_url
from src.tools.basic.jx3 import gen_ts, gen_xsk, format_body

import json

ticket = Config.jx3.api.ticket
device_id = ticket.split("::")[-1]

def get_school_id(school_name: str) -> Union[str, bool]:
    for i in force_list:
        if school_name == force_list[i]:
            return i
    return False

async def matrix_(name):
    kf = school_name_aliases(name)
    school = kungfu_to_school(kf) # type: ignore
    if name is False:
        return "此心法不存在哦~请检查后重试。"
    param = {
        "forceId": get_school_id(school), # type: ignore
        "ts": gen_ts()
    }
    param = format_body(param)
    headers = {
        "Host": "m.pvp.xoyo.com",
        "accept": "application/json",
        "deviceid": device_id,
        "platform": "ios",
        "gamename": "jx3",
        "clientkey": "1",
        "cache-control": "no-cache",
        "apiversion": "1",
        "sign": "true",
        "token": ticket,
        "Content-Type": "application/json",
        "Connection": "Keep-Alive",
        "User-Agent": "SeasunGame/178 CFNetwork/1240.0.2 Darwin/20.5.0",
        "X-Sk": gen_xsk(param)
    }
    tl_data = await post_url("https://m.pvp.xoyo.com/force/gest", data=param, headers=headers)
    tl_data = json.loads(tl_data)
    data = tl_data["data"]
    description = ""
    def fe(f, e):
        return f"{f}：{e}\n"
    for i in data:
        if i["kungfuName"] == kf:
            for x in i["zhenFa"]["descs"]:
                description = description + fe(x["name"], x["desc"])
                skillName = i["zhenFa"]["skillName"]
    return f"查到了{name}的{skillName}：\n" + description