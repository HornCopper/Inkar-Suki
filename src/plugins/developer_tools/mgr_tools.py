
from nonebot import on_notice, on_command, on_request
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, NoticeEvent, RequestEvent
from nonebot.adapters.onebot.v11 import unescape

from typing import List

from src.tools.basic import *
from src.tools.local_version import nbv

import psutil


purge = on_command("purge", priority=5)  # 清除所有`help`生成的缓存图片


@purge.handle()
async def ___(event: Event):
    if not checker(str(event.user_id), 1):
        await purge.finish(error(1))
    try:
        for i in os.listdir(CACHE):
            os.remove(CACHE + "/" + i)
    except Exception as _:
        await purge.finish("部分文件并没有找到哦~")
    else:
        await purge.finish("好的，已帮你清除图片缓存~")

shutdown = on_command("shutdown", aliases={"poweroff"}, priority=5)  # 关掉`Inkar-Suki`主程序


@shutdown.handle()
async def ____(event: Event):
    if not checker(str(event.user_id), 10):
        await shutdown.finish(error(10))
    await shutdown.send("请稍候，正在关闭中……")
    await shutdown.send("关闭成功！请联系Owner到后台手动开启哦~")
    sys.exit(0)

restart = on_command("restart", priority=5)  # 重启`Inkar-Suki`，原理为`FastAPI`的文件监控自动重启


@restart.handle()
async def _(event: Event):
    if not checker(str(event.user_id), 5):
        await restart.finish(error(5))
    with open("./src/plugins/developer_tools/example.py", mode="w") as cache:
        await restart.send("好啦，开始重启，整个过程需要些许时间，还请等我一下哦~")
        cache.write("status=\"OK\"")

echo = on_command("echo", priority=5)  # 复读只因功能


@echo.handle()
async def echo_(event: Event, args: Message = CommandArg()):
    if not checker(str(event.user_id), 9)
        await echo.finish(error(9))
    await echo.finish(args)

ping = on_command("ping", aliases={"-测试"}, priority=5)  # 测试机器人是否在线

def per_cpu_status() -> List[float]:
    return psutil.cpu_percent(interval=1, percpu=True)

def memory_status() -> float:
    return psutil.virtual_memory().percent

@ping.handle()
async def _(bot: Bot, event: Event):
    permission = checker(str(event.user_id), 1)
    if not permission:
        await ping.finish(f"咕咕咕，音卡来啦！\n当前时间为：{convert_time(getCurrentTime())}\n当前Nonebot版本为：{nbv}")
    else:
        groups = await bot.call_api("get_group_list")
        group_count = len(groups)
        friends = await bot.call_api("get_friend_list")
        friend_count = len(friends)
        registers = os.listdir(DATA)
        register_count = len(registers)
        msg = f"咕咕咕，音卡来啦！\n系统信息如下：\n当前CPU占用：{str(per_cpu_status()[0])}%\n当前内存占用：{str(memory_status())}%\n现在是：{convert_time(getCurrentTime())}\n{group_count} | {register_count} | {friend_count} | {nbv}"
    await ping.finish(msg)

post = on_command("post", priority=5)  # 发送全域公告至每一个机器人加入的QQ群。


@post.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if str(event.user_id) not in Config.owner:
        await post.finish("唔……只有机器人主人可以使用该命令哦~")
    cmd = args.extract_plain_text()
    groups = await bot.call_api("get_group_list")
    for i in groups:
        await bot.call_api("send_group_msg",
                           group_id=i["group_id"],
                           message=cmd
                           )

call_api = on_command("call_api", aliases={"api"}, priority=5)  # 调用`go-cqhttp`的`API`接口。


@call_api.handle()
async def _(event: Event, args: Message = CommandArg()):
    if not checker(str(event.user_id), 10):
        await call_api.finish(error(10))
    cmd = args.extract_plain_text()
    result = await get_url(f"{Config.cqhttp}{cmd}")
    await call_api.finish(f"已将您的接口调用完毕！")

git = on_command("-git", priority=5)  # 调用`Git`，~~别问意义是什么~~


@git.handle()
async def _(event: Event, args: Message = CommandArg()):
    if not checker(str(event.user_id), 10):
        await git.finish(error(10))
    output = ""
    commit = args.extract_plain_text()
    if commit == "pull":
        output = os.popen("git pull").read()
        await git.finish(output)
    os.system("git add .")
    msg = ""
    msg = msg + os.popen("git commit -m \""
                         + commit
                         + "\""
                         ).read()
    msg = msg + os.popen("git push").read()
    if msg == "":
        msg = "执行完成，但没有输出哦~"
    await git.finish(msg)

voice = on_command("voice", priority=5)  # 调用腾讯的语音TTS接口，生成语音。


@voice.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if not checker(str(event.user_id), 10):
        await voice.finish(error(10))
    sth = args.extract_plain_text()
    final_msg = f"[CQ:tts,text={sth}]"
    await bot.call_api("send_group_msg", group_id=event.group_id, message=final_msg)

randomnum = on_command("random_num", aliases={"随机数"}, priority=5)

@randomnum.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await randomnum.finish("唔……请参考下面的随机数生成格式：\n随机数 起始 终止")
    if not checknumber(arg[0]) or not checknumber(arg[1]):
        await randomnum.finish("唔……随机数的范围需要是数字哦~")
    num = random.randint(int(arg[0]), int(arg[1]))
    await randomnum.finish("好的，音卡已经为你生成了一个随机数：" + str(num))
