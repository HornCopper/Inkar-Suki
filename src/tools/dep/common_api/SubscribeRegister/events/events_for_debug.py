import time

from ..SubscribeItem import *


def run(__subjects: list):
    __subjects.append(SubscribeSubject("测试父事件", children_subjects=["测试事件"]))
    __subjects.append(SubscribeSubject(name="测试事件", description="用于测试事件订阅的有效性。", cron=[
        SubjectCron("* * * * *", "这是测试事件"),
        SubjectCron("* * * * *", "这是二级测试事件", level=1)
    ]))
