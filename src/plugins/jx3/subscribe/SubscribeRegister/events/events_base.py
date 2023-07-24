from ..SubscribeItem import *


def run(__subjects: list):
    __subjects.append(SubscribeSubject("玄晶", "【数据缺失，暂时关闭】当有本服的玄晶被人捡走时将发送推送。"))
    __subjects.append(SubscribeSubject("公告", "当xsj发了新公告时推送。"))
    __subjects.append(SubscribeSubject("开服", "当本服开服时推送。"))
    __subjects.append(SubscribeSubject("更新", "当xsj发了新版本时推送。"))
    __subjects.append(SubscribeSubject("818", "当本服相关的贴吧出现818帖子时推送"))
