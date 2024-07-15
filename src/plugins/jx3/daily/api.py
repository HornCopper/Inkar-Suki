from src.tools.basic import *

import datetime

async def daily_(server: str = None, group_id: str = None):
    """
    @param predict_day_num 向后预测天数
    """
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    if server is not None:
        full_link = f"{Config.jx3api_link}/data/active/calendar?num=0&server={server}&chrome=1"
    data = await get_api(full_link)
    if data["code"] == 400:
        return [PROMPT_ServerInvalid]
    data = data["data"]
    leader = "今日无世界首领"
    if "leader" in list(data):
        leader = ";".join(data["leader"])
    draw = "今日无美人图"
    if "draw" in list(data):
        draw = data["draw"]
    timestamp = datetime.datetime.strptime(data["date"], "%Y-%m-%d")
    date = convert_time(int(timestamp.timestamp()), "%Y年%m月%d日")
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
    msg = f"当前时间：{date} 星期{week}\n服务器：{server}\n大战：{war}\n战场：{battle}\n宗门：{school}\n阵营：跨服·烂柯山\n驰援：{rescue}\n首领：{leader}\n画画：{draw}\n\n【福缘宠物】\n{luck}\n【家园声望·加倍道具】\n{hometown}\n【武林通鉴·公共任务】\n{public}\n【武林通鉴·秘境任务】\n{five}\n【武林通鉴·团队秘境】\n{ten}"
    return msg