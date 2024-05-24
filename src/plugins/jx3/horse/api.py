from src.tools.basic import *

from datetime import datetime, timedelta


async def get_horse_reporter(server: str, group_id: str = None):  # 数据来源@JX3BOX
    server = server_mapping(server, group_id)
    if not server:
        return PROMPT_ServerNotExist
    final_url = f"https://next2.jx3box.com/api/game/reporter/horse?type=horse&server={server}"
    data = await get_api(final_url)
    if data["data"]["page"]["total"] == 0:
        return "没有找到该服务器信息哦，请检查后重试~"
    for i in data["data"]["list"]:
        if i["subtype"] == "npc_chat":
            time_ = convert_time(i["time"], "%m-%d %H:%M:%S")
            content = i["content"]
            map = i["map_name"]
            msg = f"{content}\n刷新时间：{time_}\n地图：{map}"
            return msg
        
async def get_horse_next_spawn(server: str):
    web_data = await get_api(f"https://next2.jx3box.com/api/game/reporter/horse?pageIndex=1&pageSize=1&server={server}&type=horse&subtype=npc_chat")
    json_data = web_data["data"]["list"][0]
    next_times = {}
    content_lines = json_data["content"].split("\n")
    for line in content_lines:
        if "距离下一匹" in line and "还有" in line:
            horse_type, time_str = line.split("还有")
            horse_type = horse_type.replace("距离下一匹", "").strip()
            time_remaining = time_str.split("分钟")[0].strip()
            next_times[horse_type] = "无法预知" if "尚久" in time_str else (datetime.fromisoformat(json_data["created_at"][:-6]) + timedelta(minutes=int(time_remaining))).strftime("%Y-%m-%d %H:%M:%S")
    result = "各马驹的下一个生成时间：\n"
    for horse, time in next_times.items():
        result += f"{horse}出世：{time}\n"

    return result.strip()