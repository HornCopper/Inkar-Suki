from src.tools.dep import *
from ..SubscribeItem import *


def init_subjects(__subjects: list[SubscribeSubject]):
    '''
    注意cron表达式中星期x范围是0-6
    '''


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
        scheduler.add_job(OnCallback, c, id=name, kwargs=kwargs)
