
from nonebot import on_notice, on_command, on_request
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, NoticeEvent, RequestEvent
from src.tools.dep import *
from src.tools.local_version import nbv
from nonebot.adapters.onebot.v11 import unescape
import psutil


purge = on_command("purge", priority=5)  # 清除所有`help`生成的缓存图片


@purge.handle()
async def ___(event: Event):
    if checker(str(event.user_id), 1) == False:
        await purge.finish(error(1))
    try:
        for i in os.listdir(bot_path.CACHE):
            os.remove(bot_path.CACHE + "/" + i)
    except Exception as _:
        await purge.finish("部分文件并没有找到哦~")
    else:
        await purge.finish("好的，已帮你清除图片缓存~")

shutdown = on_command("shutdown", aliases={"poweroff"}, priority=5)  # 关掉`Inkar-Suki`主程序


@shutdown.handle()
async def ____(event: Event):
    if checker(str(event.user_id), 10) == False:
        await shutdown.finish(error(10))
    await shutdown.send("请稍候，正在关闭中……")
    await shutdown.send("关闭成功！请联系Owner到后台手动开启哦~")
    sys.exit(0)

restart = on_command("restart", priority=5)  # 重启`Inkar-Suki`，原理为`FastAPI`的文件监控自动重启


@restart.handle()
async def _(event: Event):
    if checker(str(event.user_id), 5) == False:
        await restart.finish(error(5))
    with open("./src/plugins/developer_tools/example.py", mode="w") as cache:
        await restart.send("好啦，开始重启，整个过程需要些许时间，还请等我一下哦~")
        cache.write("status=\"OK\"")

echo = on_command("echo", priority=5)  # 复读只因功能


@echo.handle()
async def echo_(event: Event, args: v11Message = CommandArg()):
    if checker(str(event.user_id), 9) == False:
        await echo.finish(error(9))
    await echo.finish(args)

say = on_command("say", priority=5)  # 复读只因 + CQ码转换（mix：没有CQ码）


@say.handle()
async def say_(event: Event, args: v11Message = CommandArg()):
    def _unescape(message: v11Message, segment: MessageSegment):
        if segment.is_text():
            raw = unescape(str(segment))
            return message.append(raw)
        return message.append(segment)
    if checker(str(event.user_id), 10) == False:
        await say.finish(error(10))
    message = extensions.reduce(args, _unescape, v11Message())
    await say.finish(message)

ping = on_command("ping", aliases={"-测试"}, priority=5)  # 测试机器人是否在线


@ping.handle()
async def _(event: Event):
    permission = checker(str(event.user_id), 1)
    if not permission:
        times = str("现在是"
                    + DateTime().tostring()
                    + f"\nNonebot {nbv}")
        await ping.finish(times)

    def per_cpu_status() -> List[float]:
        return psutil.cpu_percent(interval=1, percpu=True)

    def memory_status() -> float:
        return psutil.virtual_memory().percent
    
    times = str("现在是"
                + DateTime().tostring()
                + f"\nNonebot {nbv}"
                )
    msg = f"咕咕咕，音卡来啦！\n系统信息如下：\n当前CPU占用：{str(per_cpu_status()[0])}%\n当前内存占用：{str(memory_status())}%\n"
    await ping.finish(msg + times)

post = on_command("post", priority=5)  # 发送全域公告至每一个机器人加入的QQ群。


@post.handle()
async def _(bot: Bot, event: Event, args: v11Message = CommandArg()):
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
async def _(event: Event, args: v11Message = CommandArg()):
    if checker(str(event.user_id), 10) == False:
        await call_api.finish(error(10))
    cmd = args.extract_plain_text()
    result = await get_url(f"{Config.cqhttp}{cmd}")
    await call_api.finish(f"已将您的接口调用完毕！")

git = on_command("-git", priority=5)  # 调用`Git`，~~别问意义是什么~~


@git.handle()
async def _(event: Event, args: v11Message = CommandArg()):
    if checker(str(event.user_id), 10) == False:
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
async def _(bot: Bot, event: GroupMessageEvent, args: v11Message = CommandArg()):
    if checker(str(event.user_id), 10) == False:
        await voice.finish(error(10))
    sth = args.extract_plain_text()
    final_msg = f"[CQ:tts,text={sth}]"
    await bot.call_api("send_group_msg", group_id=event.group_id, message=final_msg)


util_cmd_web = on_command(
    "util_web",
    name="网页截图",
    aliases={"web"},
    priority=5,
    description="网页截图，需要网址",
    catalog=permission.bot.docs,
    example=[
        Jx3Arg(Jx3ArgsType.url)
    ],
    document="""通过截图"""
)


@util_cmd_web.handle()
async def util_web(bot: Bot, event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    if checker(str(event.user_id), 10) == False:
        await util_cmd_web.finish(error(10))
    url, = args
    image = await generate_by_url(url, delay=1000)
    img = ms.image(Path(image).as_uri())
    await util_cmd_web.send(v11Message(f"{img}\n网页截图完成"))


apply = on_command(
    "apply",
    aliases={
        "申请", "领养", "购买", f"要一个{Config.name}",
        f"想要一个{Config.name}", f"想有一个{Config.name}", f"{Config.name}", "机器人",
    },
    priority=5,
    description="获取如何拉机器人入群",
    catalog=permission.mgr.group.apply,
    example=[],
    document=""""""
)


@apply.handle()
async def _(state: T_State, event: Event):
    applier = str(event.user_id)
    state["user"] = applier
    steps = [
        "音卡的好友答案为：sin y",
        "Inkar Suki用户群：650495414",
        "直接加音卡好友再邀请入群就好啦",
        "记得告诉用户群内管理哦~",
        "等待管理处理即可！"
    ]
    steps = [f"{index+1}.{x}" for (index, x) in enumerate(steps)]
    steps = str.join("\n", steps)
    await apply.finish(f"是要领养{Config.name}({bot})吗，免费的：\n{steps}")

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