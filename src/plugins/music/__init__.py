from pathlib import Path

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from nonebot.log import logger
from src.tools.utils.path import CACHE
from src.tools.utils.common import checknumber
from src.tools.generate import get_uuid

from src.plugins.sign import Sign

from .music import *
from .guess import *

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
    songs = info[0] # type: ignore
    id = info[1] # type: ignore
    platform = info[2] # type: ignore
    state["id"] = id
    state["platform"] = platform
    msg = ""
    for i in range(len(songs)):
        msg = msg + f"\n{i}." + songs[i]
    await search_music.send(msg[1:])


@search_music.got("num", prompt="输入序号即可搜索搜索歌曲，其他内容则无视~")
async def __(state: T_State, num: Message = Arg()):
    num_ = num.extract_plain_text()
    if not checknumber(num_):
        pass
    id = state["id"]
    platform = state["platform"]
    num_ = int(num_)
    song = id[num_]
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
    info = await get(platform, song_name, singer) # type: ignore
    if info == "404":
        await get_music.finish("唔……没有找到您要的歌曲~")
    platform = info[2] # type: ignore
    if platform == 1:
        p = "qq"
    else:
        p = "163"
    msg = ms.music(p, info[1]) # type: ignore
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


guess_music = on_command("guess_music", aliases={"猜歌"}, force_whitespace=True, priority=5)

@guess_music.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    # await guess_music.finish(ms.record(file=Path("C:/Users/HornCopper/Inkar-Suki/src/assets/music/1.mp3").as_uri()))
    # rd = getRandomMusic()
    # input = rd[1]
    # name = rd[0]
    # logger.info(name)
    # state["ans"] = name[:-4]
    # output = CACHE + "/" + get_uuid() + ".mp3"
    # await extract_music(input, output, 3)
    # await guess_music.send(ms.record(file=Path(output).as_uri()))
    # return

@guess_music.got("music", prompt="请告诉我歌曲名！")

async def _(event: GroupMessageEvent, state: T_State, music: Message = Arg()):
    music = music.extract_plain_text() # type: ignore
    if music == "":
        await guess_music.finish("唔……没有告诉我歌曲名哦~")
    if music == state["ans"]:
        Sign.add(str(event.user_id), 200) # type: ignore
        await guess_music.finish("恭喜你答对了！\n你获得了200枚金币！")
    else:
        Sign.reduce(str(event.user_id), 100) # type: ignore
        await guess_music.finish("唔……你答错了哦~\n你失去了100枚金币！")