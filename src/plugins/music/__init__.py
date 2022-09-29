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
        await search_music.finish("唔……参数不正确哦，只能有2个参数~")
    platform = data[0]
    song = data[1]
    info = await search(platform, song)
    if info == "404":
        await search_music.finish("唔……没有找到您要的音乐哦~")
    songs = info[0]
    id = info[1]
    platform = info[2]
    state["id"] = id
    state["platform"] = platform
    msg = ""
    for i in range(len(songs)):
        msg = msg + f"\n{i}." + songs[i]
    await search_music.send(msg[1:])
    return

@search_music.got("num", prompt="输入序号即可搜索搜索歌曲，其他内容则无视~")
async def __(state: T_State, num: Message = Arg()):
    num = num.extract_plain_text()
    if checknumber(num):
        id = state["id"]
        platform = state["platform"]
        num = int(num)
        song = id[num]
        if platform == 1:
            p = "qq"
        else:
            p = "163"
        msg = ms.music(p, song)
        await search_music.finish(msg)
    else:
        return

get_music = on_command("get_music", aliases={"点歌"}, priority=5)
@get_music.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    data = args.extract_plain_text().split(" ")
    if len(data) not in [2,3]:
        await get_music.finish("唔……参数只能有2或3个哦~")
    singer = None
    if len(data) == 3:
        singer = data[2]
    platform = data[0]
    song_name = data[1]
    info = await get(platform, song_name, singer)
    if info == "404":
        await get_music.finish("唔……没有找到您要的歌曲~")
    platform = info[2]
    if platform == 1:
        p = "qq"
    else:
        p = "163"
    msg = ms.music(p, info[1])
    await get_music.finish(msg)