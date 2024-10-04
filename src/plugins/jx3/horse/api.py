from src.utils.network import Request
from src.utils.time import Time

from datetime import datetime, timedelta

async def get_horse_reporter(server: str):  # 数据来源@JX3BOX
    final_url = f"https://next2.jx3box.com/api/game/reporter/horse?type=horse&server={server}"
    data = (await Request(final_url).get()).json()
    if data["data"]["page"]["total"] == 0:
        return "没有找到该服务器信息哦，请检查后重试~"
    for i in data["data"]["list"]:
        if i["subtype"] == "npc_chat":
            time_ = Time(i["time"]).format("%m-%d %H:%M:%S")
            content = i["content"]
            map = i["map_name"]
            msg = f"{content}\n刷新时间：{time_}\n地图：{map}"
            return msg

def is_in_current_cycle(timestamp):
    now = datetime.now()
    current_weekday = now.weekday()
    if current_weekday == 1 and now.hour < 7:
        start_of_cycle = datetime(now.year, now.month, now.day, 7) - timedelta(days=7)
    else:
        days_to_tuesday = (current_weekday - 1) % 7
        start_of_cycle = datetime(now.year, now.month, now.day, 7) - timedelta(days=days_to_tuesday)
    end_of_cycle = start_of_cycle + timedelta(days=6, hours=24)
    timestamp_dt = datetime.fromtimestamp(timestamp)
    return start_of_cycle <= timestamp_dt < end_of_cycle

def is_in_current_week(timestamp):
    now = datetime.now()
    current_weekday = now.weekday()
    if current_weekday == 0 and now.hour < 7:
        start_of_week = datetime(now.year, now.month, now.day, 7) - timedelta(days=7)
    else:
        days_to_monday = current_weekday % 7
        start_of_week = datetime(now.year, now.month, now.day, 7) - timedelta(days=days_to_monday)
    end_of_week = start_of_week + timedelta(days=7)
    timestamp_dt = datetime.fromtimestamp(timestamp)
    return start_of_week <= timestamp_dt < end_of_week

async def get_horse_next_spawn(server):
    def parse_info(raw_msg: str, flush_time: str):
        next_times = {}

        # 解析内容
        content_lines = raw_msg.split("\n")
        for line in content_lines:
            if "距离下一匹" in line and "还有" in line:
                horse_type, time_str = line.split("还有")
                horse_type = horse_type.replace("距离下一匹", "").strip()
                time_remaining = time_str.split("分钟")[0].strip()
                if "尚久" in time_str:
                    next_times[horse_type] = "无法预知"
                else:
                    created_at = datetime.strptime(flush_time, "%Y-%m-%dT%H:%M:%S+08:00")
                    next_spawn_time = created_at + timedelta(minutes=int(time_remaining))
                    time_difference = next_spawn_time - datetime.now()
                    minutes = int(time_difference.total_seconds() // 60)
                    if minutes > 0:
                        next_times[horse_type] = f"{minutes}分钟"

        # 构造结果字符串
        result = ""
        for horse, time in next_times.items():
            result += f"\n{horse[:-2]} 将于{time}后刷新"
        ans = result.strip()
        return ans if ans != "" else "时间尚久，无法预知。"
    ct_data = (await Request(f"https://next2.jx3box.com/api/game/reporter/horse?pageIndex=1&pageSize=50&server={server}&type=chitu-horse&subtype=share_msg").get()).json()
    chitu_flushed = False
    if is_in_current_cycle(ct_data["data"]["list"][0]["time"]):
        chitu_flushed = True
    dl_data = (await Request(f"https://next2.jx3box.com/api/game/reporter/horse?pageIndex=1&pageSize=50&server={server}&type=dilu-horse&subtype=share_msg").get()).json()
    dilu_flushed = False
    if is_in_current_week(dl_data["data"]["list"][0]["time"]):
        dilu_flushed = True
    web_data = (await Request(f"https://next2.jx3box.com/api/game/reporter/horse?pageIndex=1&pageSize=50&server={server}&type=horse&subtype=npc_chat").get()).json()
    msg = {}
    ft = {}
    maps = ["鲲鹏岛", "阴山大草原", "黑戈壁"]
    dl_flag = False
    for map_name in maps:
        for each_info in web_data["data"]["list"]:
            if each_info["map_name"] == map_name:
                msg[map_name] = each_info["content"]
                if each_info["content"].find("今日将有的卢出世，侠士届时可前去尝试捕捉。") != -1:
                    dl_flag = True
                ft[map_name] = each_info["created_at"]
                break
    final_msg = ""
    for map_name in maps:
        final_msg += f"\n{map_name}\n" + parse_info(msg[map_name], ft[map_name]) + "\n-------------------------------"
    final_msg = final_msg[1:-1]
    add_msg = ""
    if dilu_flushed:
        add_msg = add_msg + "\n的卢本周期内已刷新！（周期：一周）"
    else:
        add_msg = add_msg + "\n的卢本周期内未刷新！（周期：一周）"
    if chitu_flushed:
        add_msg = add_msg + "\n赤兔本周期内已刷新！（周期：周二7点至下周一7点）"
    else:
        add_msg = add_msg + "\n赤兔本周期内未刷新！（周期：周二7点至下周一7点）"
    final_msg = server + "·马场告示\n" + final_msg + "\n今日未收到的卢刷新通知！" if not dl_flag else final_msg + "\n今日将有的卢出世，敬请留意！"
    final_msg = final_msg + "\n-------------------------------" + add_msg
    return final_msg