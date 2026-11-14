from src.utils.jx3api import jx3api_get
from src.utils.time import Time

import datetime

async def get_daily_info(predict: int = 0):
    """
    获取日常信息。

    Args:
        predict (int): 向后预测天数。

    Returns:
        msg (str): 日常消息。
    """
    url = "/active/calendar"
    params = {
        "mode": "day",
        "num": predict,
    }
    data = await jx3api_get(url, params = params)
    if data["code"] != 200 or not isinstance(data["data"], dict):
        return data["msg"] or "日常查询失败，请稍后重试！"
    data = data["data"]
    leader = "今日无世界首领"
    if "leader" in data:
        leader = ";".join(data["leader"])
    timestamp = datetime.datetime.strptime(data["date"], "%Y-%m-%d")
    date = Time(int((timestamp.timestamp()))).format("%Y年%m月%d日")
    week = data["week"]
    war = data["war"]
    battle = data["battle"]
    orecar = data["orecar"]
    school = data["school"]
    rescue = data["rescue"]
    luck = ";".join(data["lucky"])
    hometown = ";".join(data["card"])
    public = ";".join(data["weekly"]["conn"])
    ten = ";".join(data["weekly"]["raid"])
    msg = f"当前时间：{date} 星期{week}\n大战：{war}\n战场：{battle}\n宗门：{school}\n阵营：{orecar}\n首领：{leader}\n驰援：{rescue}\n\n【福缘宠物】\n{luck}\n【家园声望·加倍道具】\n{hometown}\n【武林通鉴·公共任务】\n{public}\n【武林通鉴·团队秘境】\n{ten}"
    return msg
