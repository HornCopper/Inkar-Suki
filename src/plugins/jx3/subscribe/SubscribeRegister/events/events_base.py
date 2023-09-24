from ..SubscribeItem import *


def run(__subjects: list):
    __subjects.append(SubscribeSubject("玄晶", "【暂时关闭】当群聊绑定的服务器出现玄晶掉落时进行推送。"))
    __subjects.append(SubscribeSubject("公告", "当游戏官方发布游戏公告时进行推送。"))
    __subjects.append(SubscribeSubject("开服", "当群聊所绑定的服务器开服的时候进行推送。"))
    __subjects.append(SubscribeSubject("更新", "当游戏有新版本时进行推送。"))
    __subjects.append(SubscribeSubject("818", "当群聊绑定的服务器的相关的贴吧出现八卦帖子时推送。"))
    __subjects.append(SubscribeSubject("诛恶", "当群聊绑定的服务器诛恶事件触发时进行推送。"))
