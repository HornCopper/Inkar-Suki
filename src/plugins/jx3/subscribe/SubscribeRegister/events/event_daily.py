from src.plugins.jx3.daily import daily_
from ..SubscribeItem import *
from src.tools.dep import *
import threading
CACHE_Daily: dict[str, str] = {}  # day -> url_local
daily_lock = threading.Lock()


async def CallbackDaily(bot: Bot, group_id: str, sub: SubscribeSubject, cron: SubjectCron):
    global CACHE_Daily
    t = time.localtime(time.time() - 7 * 3600)   # 每天早上7点前均按前一天算
    date = time.strftime("%Y%m%d", t)
    s = ""  # 每个服日常一样，故不区分了 # getGroupServer(group_id) or "唯满侠"
    key = f"daily_{date}{s}"
    daily_lock.acquire()
    path_cache_daily = CACHE_Daily.get(key)
    if not path_cache_daily:
        # 注意销毁今天以前的缓存
        for x in CACHE_Daily:
            try:
                os.remove(CACHE_Daily.get(x))
            except:
                pass
        CACHE_Daily = {}
        url = await daily_("唯满侠", group_id, 1)  # 向后预测1天的
        img_data = httpx.get(url).content
        path_cache_daily = f"{CACHE}{os.sep}{key}.png"
        with open(path_cache_daily, "wb") as f:
            f.write(img_data)
        CACHE_Daily[key] = path_cache_daily
    daily_lock.release()
    message = f"{ms.image(Path(path_cache_daily).as_uri())}{cron.notify_content}"
    await bot.call_api("send_group_msg", group_id = group_id, message = message)

CallbackDailyToday = CallbackDaily
CallbackDailyTomorow = CallbackDaily

def run(__subjects: list):
    v = SubscribeSubject(
        name = "日常",
        description = "每天早上和晚上推送日常任务",
        children_subjects = ["今日日常", "明日日常"]
    )
    __subjects.append(v)
    v = SubscribeSubject(name = "今日日常", description = "每天一大早推送今天的日常任务", cron = [SubjectCron("50 6 * * *", "早~今天的日常来啦")], callback = CallbackDailyToday)
    __subjects.append(v)
    v = SubscribeSubject(name = "明日日常", description = "每天晚上10点推送次日的日常任务", cron = [SubjectCron("0 22 * * *", "这是明天的日常哦~晚安！")], callback = CallbackDailyTomorow)
    __subjects.append(v)
