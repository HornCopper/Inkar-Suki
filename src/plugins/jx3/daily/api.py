from src.config import Config
from src.utils.network import Request
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
    full_link = f"{Config.jx3.api.url}/data/active/calendar?num={predict}"
    data = (await Request(full_link).get()).json()
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
    luck = ";".join(data["luck"])
    hometown = ";".join(data["card"])
    public = ";".join(data["team"][0].split(";"))
    five = ";".join(data["team"][1].split(";"))
    ten = ";".join(data["team"][2].split(";"))
    msg = f"当前时间：{date} 星期{week}\n大战：{war}\n战场：{battle}\n宗门：{school}\n阵营：{orecar}\n首领：{leader}\n驰援：{rescue}\n\n【福缘宠物】\n{luck}\n【家园声望·加倍道具】\n{hometown}\n【武林通鉴·公共任务】\n{public}\n【武林通鉴·秘境任务】\n{five}\n【武林通鉴·团队秘境】\n{ten}"
    return msg