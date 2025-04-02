from src.config import Config

from src.utils.network import Request

def get_ptk(p_skey: str) -> int:
    value = 5381
    if p_skey:
        for char in p_skey:
            value += (value << 5) + ord(char)
        return value & 2147483647
    return 0

async def get_tieba_records(user_id: int) -> str:
    url = f"{Config.jx3.api.url}/data/fraud/detailed?uid={user_id}&token={Config.jx3.api.token}"
    data = (await Request(url).get()).json()
    records = data["data"]["records"]
    if not records:
        return "未找到相关记录！"
    else:
        all_records = []
        for each_record in records:
            all_records.extend(each_record["data"])
        msg = f"（共计{len(all_records)}条，已显示前{3 if len(all_records) >= 3 else len(all_records)}条）\n"
        for record in all_records[:3]:
            msg += ("标题：" + record["title"] + "\n链接：" + record["url"] + "\n")
        return msg.strip()
    

async def get_daren_count(self_id: int, user_id: int, pskey: str) -> int:
    headers = {
        "Referer": "https://cgi.vip.qq.com/",
        "Cookie": f"p_uin=o{self_id}; p_skey={pskey}"
    }

    params = {
        "ps_tk": get_ptk(pskey),
        "fuin": str(user_id)
    }

    result = (await Request("https://cgi.vip.qq.com/card/getExpertInfo", headers=headers, params=params).get()).json()
    return result["data"]["g"][1]