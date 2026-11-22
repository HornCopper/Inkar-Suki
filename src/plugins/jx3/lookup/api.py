from src.config import Config

from src.utils.jx3api import jx3api_get

async def get_tieba_records(user_id: int) -> str:
    params = {
        "uid": user_id,
        "token": Config.jx3.api.token,
    }
    url = "/fraud/detail"
    data = await jx3api_get(url, params = params)
    if data["code"] != 200:
        return data["msg"] or "骗子记录查询失败，请稍后重试！"
    if not data["data"]:
        return "未找到相关记录！"
    records = data["data"]
    msg = f"（共计{len(records)}条，已显示前{min(3, len(records))}条）\n"
    for record in records[:3]:
        msg += (f"标题：{record['title']}\n"
                f"链接：https://tieba.baidu.com/p/{record['tid']}\n")
    return msg.strip()
