from src.tools.dep import *
from src.plugins.help import css
from src.tools.generate import generate, get_uuid

lks = on_command("jx3_leader", aliases={"-烂柯山"}, priority=5)
@lks.handle()
async def _(event: GroupMessageEvent):
    bad = "https://jx3wbl.xoyocdn.com/img/icon-camp-bad.07567e9f.png"
    good = "https://jx3wbl.xoyocdn.com/img/icon-camp-good.0db444fe.png"
    def convert_time(timestamp: int):
        time_local = time.localtime(timestamp)
        dt = time.strftime("%Y年%m月%d日 %H:%M:%S", time_local)
        return dt
    def RestTime(GoalTime: int, StartTime: int = int(time.time())):
        target_date = datetime.datetime.utcfromtimestamp(GoalTime)
        delta = target_date - StartTime
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"f{days}天{hours}时{minutes}分{seconds}秒"
    def Parse(data: dict):
        pic = bad if data["camp_name"] == "恶人谷" else good
        castle = data["castle"]
        leader = data["leader"]
        status = data["str_status"]
        time_ = data["end_time"]
        rest = RestTime(time_)
        msg = f"<img src={pic}></img>{castle}<br><font color=\"darkgrey\">{leader}<br>{status}<br>{convert_time(time_)}（{rest}）</font>"
        return msg
    url = f"{Config.jx3api_link}/data/server/leader?token={token}"
    data = await get_api(url)
    chart = []
    for i in data["data"]:
        new = [i["server"], Parse(i["data"][0]), Parse(i["data"][1]), Parse(i["data"][2])]
        chart.append(new)
    html = css + tabulate(chart, tablefmt="unsafehtml")
    final_path = f"{CACHE}/{get_uuid()}.html"
    write(final_path, html)
    img = await generate(final_path, False, "table", False)
    if img == False:
        await lks.finish("唔……音卡的烂柯山图片生成失败了捏，请联系作者~")
    else:
        await lks.finish(MessageSegment.image(Path(img).as_uri()))