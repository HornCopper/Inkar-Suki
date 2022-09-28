import nonebot
import sys

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.typing import T_State

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from utils import checknumber

from .music import get, search

search_music = on_command("search_music", aliases={"搜歌"}, priority=5)
@search_music.handle()
async def _(state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    data = args.extract_plain_text().split(" ")
    if len(data) != 2:
        await search_music.finish("唔……只能有两个参数哦~")
    platform = data[0]
    music_platform_type = False
    song = data[1]
    if platform in ["QQ","QQ音乐","qq","q","Q","tx","tc","tencent","腾讯","腾讯音乐","qq音乐","Qq","Qq音乐","qQ","qQ音乐"]:
        info = await search(True, song)
        music_platform_type = True
    elif platform in ["网易","163","网抑云","网抑","网","netease","n","网易云音乐","网抑云音乐"]:
        info = await search(False, song)
    else:
        await search_music.finish("唔……这是什么平台呢？")
    state["id"] = info[1]
    state["platform"] = music_platform_type
    msg = ""
    for i in range(info[0]):
        msg = msg + "\n" + str(i) + "." + info[0][i]
    msg = msg[1:]
    await search_music.send(msg)
    return

@search_music.got("num", prompt="输入序号即可搜索搜索歌曲，其他内容则无视~")
async def __(state: T_State, num: Message = Arg()):
    num = num.extract_plain_text()
    if checknumber(num) != True:
        return
    else:
        num = int(num)
        id = state["id"]
        platform = state["platform"]
        if platform:
            type_ = "qq"
        else:
            type_ = "163"
        msg = ms.music(type_, id[num])
        await search_music.finish(msg)

get_music = on_command("get_music", aliases={"点歌"}, priority=5)
@get_music.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    data = args.extract_plain_text().split(" ")
    if len(data) not in [2,3]:
        await get_music.finish("唔……只能有两个或者三个参数哦~")
    platform = data[0]
    music_platform_type = False
    song = data[1]
    singer = None
    if len(data) == 3:
        singer = data[2]
    else:
        singer = None
    if platform in ["QQ","QQ音乐","qq","q","Q","tx","tc","tencent","腾讯","腾讯音乐","qq音乐","Qq","Qq音乐","qQ","qQ音乐"]:
        info = await get(True, song, singer)
        music_platform_type = True
    elif platform in ["网易","163","网抑云","网抑","网","netease","n","网易云音乐","网抑云音乐"]:
        info = await get(False, song, singer)
    else:
        await get_music.finish("唔……这是什么平台呢？")
    if type(info) == type("sb"):
        await get_music.finish(info)
    else:
        if music_platform_type:
            type_ = "qq"
        else:
            type_ = "163"
        msg = ms.music(type_, info)
        await get_music.finish(msg)