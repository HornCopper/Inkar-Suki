import copy
from typing import overload, Callable
from cron_descriptor import Options, CasingTypeEnum, DescriptionTypeEnum, ExpressionDescriptor
import croniter


def convert_keywords(raw: str) -> str:
    week_seriers = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    i18n_seriers = ['Monday', 'Tuesday', 'Wednesday',
                    'Thursday', 'Friday', 'Saturday', 'Sunday']
    seri_len = len(week_seriers)
    for index, x in enumerate(i18n_seriers):
<<<<<<< HEAD
        target = index + 1  # 似乎i18n将0认为是周日了
=======
        # target = index + 1  # 似乎i18n将0认为是周日了
        target = index # 全文需要注意已通过cron表达式dayofweek为mon,tue等字符串
>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0
        raw = raw.replace(x, week_seriers[target % seri_len])
    return raw


class SubjectCron:
    @overload
    def __init__(self, exp: str, notify: str = None, level: int = 0) -> None:
        '''
        @param expression CRON-exp
            year (int|str) – 4-digit year
            month (int|str) – month (1-12)
            day (int|str) – day of month (1-31)
            week (int|str) – ISO week (1-53)
            day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
            hour (int|str) – hour (0-23)
            minute (int|str) – minute (0-59)
            second (int|str) – second (0-59)
        @param notify will pass to callback
        @param level will pass to callback
        '''
        ...

    @overload
    def __init__(self, exp: str, notify: callable = None, level: int = 0) -> None:
        ...

    def __init__(self, exp: str, notify=None, level: int = 0) -> None:
        self.expression = exp
        self.notify = notify
        self.level = level

    @property
    def notify_content(self):
        r = '无效的推送信息，清检查。'
        if isinstance(self.notify, Callable):
            r = self.notify()
        elif isinstance(self.notify, str):
            r = str(self.notify)
        return r

    @property
    def cron_description(self):
        options = Options()
        options.casing_type = CasingTypeEnum.Sentence
        options.use_24hour_time_format = True
        options.locale_code = 'zh_CN'
        descriptor = ExpressionDescriptor(self.expression, options)
        result = descriptor.get_description(DescriptionTypeEnum.FULL)
        return convert_keywords(result)

    @property
    def cron_get_time(self) -> tuple[int, int]:
        '''
        获取上次和下次执行的时间戳
        '''
        cron = croniter.croniter(self.expression)
        return (cron.get_prev() * 1e3, cron.get_next() * 1e3)

    def to_dict(self):
        r = copy.deepcopy(self.__dict__)
        r['cron_description'] = self.cron_description
        r['notify_content'] = self.notify_content
        x_time = self.cron_get_time
        r['next_time'] = x_time[1]
        r['prev_time'] = x_time[0]
        return r


class SubscribeSubject:
    def __init__(self, name: str, description: str = None, children_subjects: list = None, cron: list[SubjectCron] = None, callback: callable = None) -> None:
        self.name = name
        self.description = description
        self.children = [] if not children_subjects else children_subjects
        self.cron = cron
        self.callback = callback
        self.user_args: dict = None  # 用户自定义数据

    def set_user_args(self, v: dict):
        '''
        设置用户参数
        '''
        self.user_args = v

    def to_dict(self):
        v = copy.deepcopy(self.__dict__)
        n_crons = 'cron'
        crons = v.get(n_crons)
        if crons:
            crons = [x.to_dict() for x in crons]
        v[n_crons] = crons

        n_callback = 'callback'
        callback = v.get(n_callback)
        v[n_callback] = callback and callback.__name__

        return v
