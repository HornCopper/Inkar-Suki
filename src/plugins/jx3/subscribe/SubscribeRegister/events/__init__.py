from src.tools.dep import *
from ..SubscribeItem import *
from ..callback import *


def init_subjects(__subjects: list[SubscribeSubject]):
    '''
    注意cron表达式中星期x范围是0-6或直接使用 SUN, MON, TUE, WED, THU, FRI , SAT
    '''
    from . import events_base
    events_base.run(__subjects)
    # from . import events_for_debug
    # events_for_debug.run(__subjects)
    from . import events_gf
    events_gf.run(__subjects, OnGfBig, OnGfSmall)
    from . import events_world_boss
    events_world_boss.run(__subjects, OnWorldBoss)
    from . import event_daily
    event_daily.run(__subjects)

def init_cron(sub: SubscribeSubject, OnCallback: callable):
    if not sub.cron:
        return

    for index, cron in enumerate(sub.cron):
        name = f'{sub.name}@{index}'
        if not len(cron.expression.split(' ')) == 5:
            return logger.warn(f'subscriber get invalid cron expression:{cron.expression}')
        c = CronTrigger.from_crontab(cron.expression)
        v = f'subscriber register:{name} on cron-exp:[{cron.expression}]'
        logger.info(v)
        kwargs = {'sub': sub, 'cron': cron, }
        job = scheduler.add_job(OnCallback, c, id=name, kwargs=kwargs)
        pass
