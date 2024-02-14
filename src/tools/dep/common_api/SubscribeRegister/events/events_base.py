from ..SubscribeItem import *


def run(__subjects: list):
    __subjects.append(SubscribeSubject("玄晶", "当群聊绑定的服务器出现玄晶掉落时进行推送。"))
    __subjects.append(SubscribeSubject("抓马", "当群聊绑定的服务器出现马驹刷新时进行推送。"))
    __subjects.append(SubscribeSubject("奇遇", "当群聊绑定的服务器出现奇遇触发时进行推送。"))
    __subjects.append(SubscribeSubject("追魂", "当群聊绑定的服务器出现追魂点名时进行推送。"))
    __subjects.append(SubscribeSubject("的卢", "当群聊绑定的服务器出现的卢预告、刷新、捕获、竞拍时进行推送。"))
    __subjects.append(SubscribeSubject("扶摇", "当群聊绑定的服务器出现扶摇试炼时进行推送，会同时播报点名。"))
    __subjects.append(SubscribeSubject("关隘", "云从社特定时间更新推送预告。"))
    __subjects.append(SubscribeSubject("公告", "当游戏官方发布游戏公告时进行推送。"))
    __subjects.append(SubscribeSubject("开服", "当群聊所绑定的服务器开服的时候进行推送。"))
    __subjects.append(SubscribeSubject("更新", "当游戏有新版本时进行推送。"))
    __subjects.append(SubscribeSubject("818", "当贴吧出现八卦帖子时推送。"))
    __subjects.append(SubscribeSubject("诛恶", "当群聊绑定的服务器诛恶事件触发时进行推送。"))
    __subjects.append(SubscribeSubject("云从", "云从社特定时间更新推送预告。"))