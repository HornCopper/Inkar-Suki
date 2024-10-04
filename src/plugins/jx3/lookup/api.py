from src.utils.network import Request

def get_ptk(p_skey: str) -> int:
    value = 5381
    if p_skey:
        for char in p_skey:
            value += (value << 5) + ord(char)
        return value & 2147483647
    return 0

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