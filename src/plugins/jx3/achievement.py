# 奇遇系统
# 开始施工
# 完成方法：https://helper.jx3box.com/api/wiki/post?client=std&supply=1&type=achievement&source_id=10140  source_id为奇遇id，用于标识 getAchievementFinishMethod
# 奇遇记录：https://pull.j3cx.com/api/serendipity?server=%E5%B9%BD%E6%9C%88%E8%BD%AE&start=0&pageIndex=1&pageSize=60 server为服务器
# 获取奇遇ID：https://data.jx3box.com/pvx/serendipity/output/serendipity.json 短数字拼接URL，长数字用于标识 getLongNumByShortNum
# 获取奇遇列表：https://node.jx3box.com/serendipities?per=93&page=1 将用户输入的字符串进行检索 找出短数字 getShortNum

# 题外话，奇穴：https://data.jx3box.com/bps/v1/22/talent.json

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
    short_num = await getShortNum(Achievement)
    if short_num == False:
        return "奇遇不存在哦，请检查后重试~\n若游戏中只显示为“宠物奇缘”，则请使用奇遇ID搜索。\n奇遇ID是魔盒中打开某一奇遇页面后，网址的最后三个数字。\n唔……ID搜索奇遇暂时不支持获取图片哦~"
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
            