from ..SubscribeItem import *


def run(__subjects: list, OnWorldBoss: callable):
    tip_world_boss = '世界boss活动将在20:00开始，按下Ctrl+Z去烂柯山或者前尘地图看看吧'
    tip_world_boss_start = '世界boss活动开始啦，按下Ctrl+Z去烂柯山或者前尘地图看看吧'
    __subjects.append(SubscribeSubject(
        name='世界boss',
        description='每周三周五晚上20:00通过烂柯山进入世界boss，可以晚点去这样不用排队哦。',
        cron=[
            SubjectCron('30 19 * * 2', tip_world_boss, level=1),
            SubjectCron('30 19 * * 4', tip_world_boss, level=1),
            SubjectCron('0 20 * * 2', tip_world_boss_start),
            SubjectCron('0 20 * * 4', tip_world_boss_start),
        ],
        callback=OnWorldBoss,
    ))
