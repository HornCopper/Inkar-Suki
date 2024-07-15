from .music import get, search, getLyricBelongToMusicInfo
from src.tools.utils import checknumber

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.typing import T_State



"""
搜歌可查询歌曲，点歌直接根据歌曲名和作者（若有）推出歌曲。

数据来源：
@网易云音乐
@QQ音乐
"""

search_music = on_command("search_music", aliases={"搜歌"}, force_whitespace=True, priority=5)


@search_music.handle()
async def _(state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
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


@search_music.got("num", prompt="输入序号即可搜索搜索歌曲，其他内容则无视~")
async def __(state: T_State, num: Message = Arg()):
    num = num.extract_plain_text()
    if not checknumber(num):
        pass
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

get_music = on_command("get_music", aliases={"点歌"}, force_whitespace=True, priority=5)


@get_music.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    data = args.extract_plain_text().split(" ")
    if len(data) not in [2, 3]:
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

get_lyrics = on_command("get_lyrics", aliases={"搜歌词"}, force_whitespace=True, priority=5)


@get_lyrics.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    lyrics = args.extract_plain_text()
    if lyrics == "":
        await get_lyrics.finish("唔……没有告诉我歌词哦~")
    await get_lyrics.finish(await getLyricBelongToMusicInfo(lyrics))
