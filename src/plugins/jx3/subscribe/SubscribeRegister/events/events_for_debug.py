import time

from ..SubscribeItem import *


def run(__subjects: list):
    __subjects.append(SubscribeSubject("测试父事件", children_subjects=["测试事件"]))

    def test_event(v: str):
        def x():
            s = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            return v.format(time=s)
        return x
    __subjects.append(SubscribeSubject(name="测试事件", description="用于测试事件订阅的有效性。", cron=[SubjectCron(
        "* * * * *", test_event("这是测试事件{time}的返回值")), SubjectCron("* * * * *", test_event("这是二级测试事件{time}的返回值"), level=1)]))
