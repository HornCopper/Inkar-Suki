from ..SubscribeItem import *


def run(__subjects: list):
    __subjects.append(SubscribeSubject("玄晶", "【暂时关闭】当群聊绑定的服务器出现玄晶掉落时进行推送。"))
    __subjects.append(SubscribeSubject("公告", "当游戏官方发布游戏公告时进行推送。"))
    __subjects.append(SubscribeSubject("开服", "当群聊所绑定的服务器开服的时候进行推送。"))
    __subjects.append(SubscribeSubject("更新", "当游戏有新版本时进行推送。"))
    __subjects.append(SubscribeSubject("818", "当贴吧出现八卦帖子时推送。"))
    __subjects.append(SubscribeSubject("诛恶", "【暂时关闭】当群聊绑定的服务器诛恶事件触发时进行推送。"))
    __subjects.append(SubscribeSubject("云从", "推送云从社预告。"))


def run_after(__subjects: list):
    """加载完成其他后加载此处"""
    __subjects.append(SubscribeSubject("机器人更新", "当机器人有新的更新时推送。"))
    __subjects.append(SubscribeSubject("机器人风控", "当有机器人被风控时推送"))
