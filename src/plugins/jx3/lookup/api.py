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
    params = {
        "uid": user_id,
        "token": Config.jx3.api.token,
    }
    url = f"{Config.jx3.api.url}/fraud/detail"
    data = (await Request(url, params = params).get()).json()
    if not data["data"]:
        return "未找到相关记录！"
    records = data["data"]
    msg = f"（共计{len(records)}条，已显示前{min(3, len(records))}条）\n"
    for record in records[:3]:
        msg += (f"标题：{record['title']}\n"
                f"链接：https://tieba.baidu.com/p/{record['tid']}\n")
    return msg.strip()

async def get_daren_count(self_id: int, user_id: int, pskey: str) -> str:
    headers = {
        "Referer": "https://cgi.vip.qq.com/",
        "Cookie": f"p_uin=o{self_id}; p_skey={pskey}",
    }

    params = {
        "ps_tk": get_ptk(pskey),
        "fuin": str(user_id),
    }

    try:
        result = (
            await Request(
                "https://cgi.vip.qq.com/card/getExpertInfo",
                headers = headers,
                params = params,
            ).get()
        ).json()
    except Exception:
        return "未知"
    return str(result["data"]["g"][1])
