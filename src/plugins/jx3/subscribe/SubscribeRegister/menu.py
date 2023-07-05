from src.tools.dep import *
from .SubscribeItem import *
from .callback import *
__X = SubscribeSubject


def __init_subjects(__subjects: list[__X]):
    '''
    注意cron表达式中星期x范围是0-6
    '''
    __subjects.append(__X('玄晶'))
    __subjects.append(__X('公告'))
    __subjects.append(__X('开服'))
    __subjects.append(__X('更新'))
    __subjects.append(__X('818'))

    __subjects.append(__X('攻防', '含大攻防和小攻防', ['大攻防', '小攻防']))
    __subjects.append(__X(
        name='大攻防',
        description='每周六日中午12:30，晚上18:30分别排恶人谷和浩气盟主战场。',
        cron=[
            SubjectCron('20 12 * * 5',
                        '攻防排队12:30要开始啦，快去主城准备排恶人谷吧~奇袭战场可以提前排队哦'),
            SubjectCron('20 18 * * 5',
                        '攻防排队18:30要开始啦，快去主城准备排恶人谷吧~奇袭战场可以提前排队哦'),
            SubjectCron('20 12 * * 6',
                        '攻防排队12:30要开始啦，快去主城准备排浩气盟吧~奇袭战场可以提前排队哦'),
            SubjectCron('20 18 * * 6',
                        '攻防排队18:30要开始啦，快去主城准备排浩气盟吧~奇袭战场可以提前排队哦'),
        ],
    ))

    __subjects.append(__X(
        name='小攻防',
        description='每周二周四晚上18:30排队争夺的地图，可输入[沙盘 区服]查看当前争夺图。',
        cron=[
            SubjectCron('20 19 * * 1', '攻防排队18:30要开始啦，快去过图点准备卡图吧'),
            SubjectCron('20 19 * * 3', '攻防排队18:30要开始啦，快去过图点准备卡图吧'),
        ],
    ))

    tip_world_boss = '世界boss活动将在20:00开始，按下ctrl+z去烂柯山或者前尘地图看看吧'
    tip_world_boss_start = '世界boss活动开始啦，按下ctrl+z去烂柯山或者前尘地图看看吧'
    __subjects.append(__X(
        name='世界boss',
        description='每周三周五晚上20:00通过烂柯山进入世界boss，可以晚点去这样不用排队哦。',
        cron=[
            SubjectCron('30 19 * * 2', tip_world_boss, level=1),
            SubjectCron('30 19 * * 4', tip_world_boss, level=1),
            SubjectCron('0 20 * * 2', tip_world_boss_start),
            SubjectCron('0 20 * * 4', tip_world_boss_start),
        ],
    ))


def __init_cron(sub: __X):
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


def load_subjects(__subjects: list[__X], target: dict[str, __X]):
    '''
    从预设逻辑中初始化
    @param __subjects 初始化主题到列表
    @param target 初始化主题到字典
    '''
    __init_subjects(__subjects)
    for sub in __subjects:
        target[sub.name] = sub
        __init_cron(sub)
