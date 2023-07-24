from ..SubscribeItem import *


def run(__subjects: list, OnGfBig: callable, OnGfSmall: callable):
    __subjects.append(SubscribeSubject("攻防", "含大攻防和小攻防", ["大攻防", "小攻防"]))
    __subjects.append(SubscribeSubject(name="大攻防", description="每周六日中午12:30，晚上18:30分别排浩气盟和恶人谷主战场。", cron=[SubjectCron("20 12 * * SAT", "攻防排队12:30要开始啦，快去主城准备排浩气盟吧~奇袭战场可以提前排队哦"), SubjectCron(
        "20 18 * * SAT", "攻防排队18:30要开始啦，快去主城准备排浩气盟吧~奇袭战场可以提前排队哦"), SubjectCron("20 12 * * SUN", "攻防排队12:30要开始啦，快去主城准备排恶人谷吧~奇袭战场可以提前排队哦"), SubjectCron("20 18 * * SUN", "攻防排队18:30要开始啦，快去主城准备排恶人谷吧~\n奇袭战场可以提前排队哦")], callback=OnGfBig))
    __subjects.append(SubscribeSubject(name="小攻防", description="每周二周四晚上18:30排队争夺的地图，可输入[沙盘 区服]查看当前争夺图。", cron=[SubjectCron("20 19 * * TUE", "攻防排队19:30要开始啦，快去过图点准备卡图吧！"), SubjectCron(
        "20 19 * * THU", "攻防排队19:30要开始啦，快去过图点准备卡图吧！"), SubjectCron("0 19 * * TUE", "攻防排队19:30要开始啦，快去过图点准备卡图吧！", 1), SubjectCron("0 19 * * THU", "攻防排队19:30要开始啦，快去过图点准备卡图吧！", 1)], callback=OnGfSmall))
