import asyncio
import httpx
import nonebot
import os
import sys
import json

from configparser import ConfigParser
from enum import IntEnum
from itertools import dropwhile
from nonebot.adapters.onebot.v11 import Bot

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
DATA = TOOLS[:-5] + "data"

from file import read
from config import Config

UpdatePackageUrls = "https://jx3hdv4.autoupdate.kingsoft.com/jx3hd_v4/zhcn_hd/"

class SizeUnit(IntEnum):
    B = 1 << 10
    KB = 1 << 20
    MB = 1 << 30
    GB = 1 << 40

async def package_size(session: httpx.AsyncClient, patch_url: str) -> int:
    async with session.head(f"{UpdatePackageUrls}{patch_url}") as resp:
        return int(resp.headers["Content-Length"])

async def update_patch_checker(bot: Bot, parser: ConfigParser = ConfigParser()) -> None:
    async with httpx.AsyncClient(timeout=10, verify = False) as session:
        resp = await session.get(f"{UpdatePackageUrls}autoupdateentry.txt")
        content = resp.text
        parser.read_string(content)
        CURRENT_VERSION = parser["version"]["LatestVersion"]
        while True:
            resp = await session.get(f"{UpdatePackageUrls}autoupdateentry.txt")
            parser.read_string(resp.text)
            if (new_version := parser["version"]["LatestVersion"]) > CURRENT_VERSION:
                patchs = [patch for patch in dropwhile(lambda x: not (x.startswith(f"jx3hd_v4_c_{CURRENT_VERSION}")), parser["PatchList"].values()) if patch.endswith("exe")]
                size = sum(await asyncio.gather(*[package_size(session, patch) for patch in patchs]))
                if size < SizeUnit.B:
                    size = f"{size:.2f} B"
                elif size < SizeUnit.KB:
                    size = f"{size / SizeUnit.B:.2f} KB"
                elif size < SizeUnit.MB:
                    size = f"{size / SizeUnit.KB:.2f} MB"
                elif size < SizeUnit.GB:
                    size = f"{size / SizeUnit.MB:.2f} GB"
                msg = f"更新来啦！\n客户端版本 {CURRENT_VERSION} -> {new_version}\n本次更新共 {len(patchs)} 个更新包\n总计 {size}"
                groups = os.listdir(DATA)
                for i in groups:
                    subscribe = json.loads(read(DATA + "/" + i + "/subscribe.json"))
                    if ["更新"] in subscribe:
                        await bot.call_api("send_group_msg", group_id = int(i), message = msg)
                CURRENT_VERSION = new_version
            await asyncio.sleep(30)

async def main():
    bots: list = Config.bot
    for i in bots:
        bot = nonebot.get_bot(i)
        await update_patch_checker(bot)

asyncio.run(main())