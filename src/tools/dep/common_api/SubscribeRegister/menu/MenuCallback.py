from .BaseMenuCallback import *
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


load_subjects(__subjects, VALID_Subjects)


class MenuCallback(BaseMenuCallback):
    @staticmethod
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

    @staticmethod
    def check_subscribed(target_subject: SubscribeSubject, user_subs: dict[str, dict], sub_from: SubscribeSubject = None) -> tuple[bool, SubscribeSubject]:
        """
        检查当前订阅是否已包含
        @return tuple[
            当前监听参数值，-1表示未监听
            订阅的来源
        ]
        """
        if isinstance(target_subject, SubscribeSubject):
            target_subject = target_subject.name

        def get_user_arg(v):
            return get_number(v.get("arg"))
        v = user_subs.get(target_subject)
        if v is not None:  # 数值
            return get_user_arg(v), sub_from or target_subject

        result = -1
        for s in user_subs:
            u_sub = VALID_Subjects.get(s)  # 获取当前项
            if u_sub is None:
                continue
            cur_value = user_subs.get(s) or {}
            # 子项继承父项的事件等级
            children_value = dict([[x, cur_value] for x in u_sub.children])
            # 逐个检查子项，并选择其中监听等级最高的返回，默认返回-1
            sub_level, _ = MenuCallback.check_subscribed(
                target_subject, children_value, sub_from)
            if not isinstance(sub_level, int):
                sub_level = get_user_arg(sub_level)
            if result < sub_level:
                result = sub_level
                sub_from = u_sub
        return result, sub_from
