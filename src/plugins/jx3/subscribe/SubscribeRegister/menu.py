from src.tools.dep import *

from .SubscribeItem import *
from .events import *

# 订阅 主题 订阅等级
__subjects: list[SubscribeSubject] = []
VALID_Subjects: dict[str, SubscribeSubject] = {}

def load_subjects(__subjects: list[SubscribeSubject], target: dict[str, SubscribeSubject]):
    """
    从预设逻辑中初始化
    @param __subjects 初始化主题到列表
    @param target 初始化主题到字典
    """
    init_subjects(__subjects)
    logger.info(f"subscribes inited: count {len(__subjects)}")
    for sub in __subjects:
        target[sub.name] = sub
        init_cron(sub, OnCallback)

def check_subscribed(sub: SubscribeSubject, user_subs: dict[str, dict]) -> bool:
    """
    检查当前订阅是否已包含
    @return 返回当前监听参数值，-1表示未监听
    """
    def get_user_arg(v):
        return get_number(v.get("arg"))
    v = user_subs.get(sub.name)
    if not v is None:
        return get_user_arg(v)
    result = -1
    for s in user_subs:
        u_sub = VALID_Subjects.get(s)  # 获取当前项
        if u_sub is None:
            continue
        cur_value = user_subs.get(s) or {}
        # 子项继承父项的事件等级
        children_value = dict([[x, cur_value] for x in u_sub.children])
        # 逐个检查子项，并选择其中监听等级最高的返回，默认返回-1
        v = check_subscribed(sub, children_value)
        if not isinstance(v, int):
            v = get_user_arg(v)
        if result < v:
            result = v
    return result

def get_subscribe_items(user_subs: dict[str, dict]):
    """
    将当前订阅转换为实体
    """
    r = []
    for x in user_subs:
        v = VALID_Subjects.get(x)
        if not v:
            continue
        v.set_user_args(user_subs.get(x))
        r.append(v)
    return r

async def OnCallback(sub: SubscribeSubject, cron: SubjectCron):
    result = []
    bots = get_driver().bots
    for botname in bots:
        bot = bots.get(botname)
        for group in await bot.call_api("get_group_list"):
            group_id = group.get("group_id")
            g_subscribe = load_or_write_subscribe(group_id)
            u_subscribed_level = check_subscribed(sub, g_subscribe)
            can_send = u_subscribed_level >= cron.level
            result.append([botname, group_id, can_send])
            if not can_send:
                continue
            func = sub.callback if sub.callback else OnDefaultCallback
            await func(bot, group_id, sub, cron)
    valid = len([x for x in result if x[2]])
    total = len(result)
    pre = f"send events:{sub.name}[{cron.notify_content}] to "
    logger.debug(f"{pre}{valid}/{total} groups")

load_subjects(__subjects, VALID_Subjects)
