import os, sys, psutil, nonebot
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from typing import List
from .example import status
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
from permission import checker, error
from file import read, write
from config import Config
from http_ import http
from functools import reduce
from nonebot.adapters.onebot.v11 import Message, MessageSegment, unescape, Event, Bot

helpimg = on_command("helpimg", aliases={"hi"}, priority=5)


@helpimg.handle()
async def _(event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id), 9) == False:
        await helpimg.finish(error(10))
    size = args.extract_plain_text()
    if size:
        if size.find("x"):
            write(Config.size,size)
            await helpimg.finish("好的~图片尺寸已修改为"+size+"。")
        else:
            await helpimg.finish("唔，这尺寸不对哦~")
    else:
        await helpimg.finish("唔，你忘记输入尺寸了啦！")
    
imgsize = on_command("imgsize",aliases={"is"},priority=5)

@imgsize.handle()
async def __(bot: Bot, event: Event):
    if checker(str(event.user_id),9) == False:
        await bot.finish(error(9))
    size = read(Config.size_path)
    await imgsize.finish("查到啦！当前图片尺寸为"+size+"。")
purge = on_command("purge",priority=5)

@purge.handle()
async def ___(event: Event):
    if checker(str(event.user_id),1) == False:
        await purge.finish(error(1))
    if Config.platform == True:
        os.system(f"rm -rf {Config.help_image_save_to}")
        os.system(f"rm -rf {Config.html_path}")
    else:
        os.system(f"rd /s /q {Config.help_image_save_to}")
        os.system(f"rd /s /q {Config.html_path}")
    await purge.finish("好的，已帮你清除图片缓存~")

shutdown = on_command("shutdown",aliases={"poweroff"},priority=5)

@shutdown.handle()
async def ____(event: Event):
    if checker(str(event.user_id),10) == False:
        await shutdown.error(10)
    if Config.platform == False:
        await shutdown.finish("唔，主人用了Windows，我没办法关闭哦~")
    await shutdown.send("请稍候，正在关闭中……")
    await shutdown.send("关闭成功！请联系Owner到后台手动开启哦~")
    os.system("killall nb")

restart = on_command("restart",priority=5)
@restart.handle()
async def _(event: Event):
    with open("./example.py",mode="w") as cache:
        if checker(str(event.user_id),5) == False:
            await restart.finish(error(5))
        await  restart.send("好啦，开始重启，整个过程需要些许时间，还请等我一下哦~")
        cache.write("status=\"OK\"")

echo = on_command("echo",priority=5)
@echo.handle()
async def echo_(event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),9) == False:
        await echo.finish(error(9))
    await echo.finish(args)
say = on_command("say",priority=5)
@say.handle()
async def say_(event: Event, args: Message = CommandArg()): 
    def _unescape(message: Message, segment: MessageSegment):
        if segment.is_text():
            return message.append(unescape(str(segment)))
        return message.append(segment)
    if checker(str(event.user_id),9) == False:
        await say.finish(error(9))
    message = reduce(_unescape, args, Message())
    await say.finish(message)
ping = on_command("ping", aliases={"测试"}, priority=5)
@ping.handle()
async def _(event: Event):
    if block(str(event.user_id)):
        return
    if checker(str(event.user_id), 1) == False:
        times = str("现在是" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + f"\n当前版本v{Config.version}(Nonebot 2.0.0b2)")
        await ping.finish(times)
    def per_cpu_status() -> List[float]:
        return psutil.cpu_percent(interval=1, percpu=True)
    def memory_status() -> float:
        return psutil.virtual_memory().percent
    times = str("现在是" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + f"\n当前版本v{Config.version}(Nonebot 2.0.0b2)")
    msg = f"来啦！\n系统信息如下：\nCPU占用：{str(per_cpu_status()[0])}%\n内存占用：{str(memory_status())}%\n"
    await ping.finish(msg + times)
back = on_command("back", priority=5)
@back.handle()
async def back_(event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id), 10) == False:
        await back.finish(error(10))
    os.system(args.extract_plain_text())
    await back.finish("好啦，执行完毕！")
front = on_command("front",priority=5)
@front.handle()
async def front_(event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),10) == False:
        await front.finish(error(10))
    msg = os.popen(args.extract_plain_text()).read()
    await front.finish(f"{msg}")
post = on_command("post", aliases={"公告"}, priority=5)
@post.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id), 10) == False:
        post.finish(error(10))
    cmd = args.extract_plain_text()
    groups = await bot.call_api("get_group_list")
    for i in groups:
        await bot.call_api("send_group_msg",group_id=i["group_id"],message=f"[开发者全域公告]{cmd}")
call_api = on_command("call_api",aliases={"api"},priority=5)
@call_api.handle()
async def _(event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),10) == False:
        await call_api.finish(error(10))
    cmd = args.extract_plain_text()
    await http.get_url(f"{Config.cqhttp}{cmd}")