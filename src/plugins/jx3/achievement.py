import os
import sys
import re
import nonebot
from pathlib import Path
from nonebot.adapters.onebot.v11 import MessageSegment
from bs4 import BeautifulSoup
from xpinyin import Pinyin
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
ASSETS = TOOLS[:-5] + "assets"
PLUGINS = TOOLS[:-5] + "plugins"
from utils import get_api, get_content, get_status, checknumber

async def get_achievement(Achievement: str):
    achievement_image_path = ASSETS + "/jx3/achievement/" + Achievement + ".png"
    if os.path.exists(achievement_image_path):
        return achievement_image_path
    else:
        final_url = f"https://img.jx3box.com/adventure/adventure/std/reward/open/{Achievement}_open.png"
        if await get_status(final_url) == 404:
            p = Pinyin()
            pinyin = p.get_pinyin(Achievement).replace("-","")
            final_url = f"https://img.jx3box.com/adventure/adventure/std/reward/open/{pinyin}_open.png"
        cache = open(achievement_image_path, mode = "wb")
        image = await get_content(final_url)
        cache.write(image)
        cache.close()
        return achievement_image_path

async def getLongNumByShortNum(ShortNum: str):
    info = await get_api("https://data.jx3box.com/pvx/serendipity/output/serendipity.json")
    result = info[ShortNum]
    return result

async def getAchievementFinishMethod(Achievement: str):
    if checknumber(Achievement):
        short_num = Achievement
        long_num = await getLongNumByShortNum(str(short_num))
        final_url = f"https://helper.jx3box.com/api/wiki/post?client=std&supply=1&type=achievement&source_id={long_num}"
        method = await get_api(final_url)
        info = method["data"]["post"]["content"]
        info = BeautifulSoup(re.sub(r"<img.*?(?:>|\/>)", "", info[info.find("<p>.</p>") + 8:]),"html.parser").get_text()
        info = re.sub(r"\\.*" , "", info)
        info = re.sub(r"\n*\n", "\n", info)
        if info[-1] == "\n":
            info = info[:-1]
        return info
    else:
        short_num = await getShortNum(Achievement)
        if short_num == False:
            return "数据库中查不到这个奇遇，很有可能是数据的问题，可尝试使用ID搜索~\n若游戏中只显示为“宠物奇缘”，则请使用奇遇ID搜索。\n奇遇ID是魔盒中打开某一奇遇页面后，网址的最后三个数字。\n唔……ID搜索奇遇暂时不支持获取图片哦~"
        long_num = await getLongNumByShortNum(str(short_num))
        final_url = f"https://helper.jx3box.com/api/wiki/post?client=std&supply=1&type=achievement&source_id={long_num}"
        method = await get_api(final_url)
        info = method["data"]["post"]["content"]
        info = BeautifulSoup(re.sub(r"<img.*?(?:>|\/>)", "", info[info.find("<p>.</p>") + 8:]),"html.parser").get_text()
        info = re.sub(r"\\.*" , "", info)
        info = re.sub(r"\n*\n", "\n", info)
        if info[-1] == "\n":
            info = info[:-1]
        info = MessageSegment.image(Path(await get_achievement(Achievement)).as_uri()) + "\n" + info
        return info

async def getShortNum(achievement: str):
    achievements = await get_api("https://node.jx3box.com/serendipities?per=93&page=1")
    for i in achievements["list"]:
        if i["szName"] == achievement:
            return i["dwID"]
    return False
            