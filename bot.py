#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from src.tools.config import Config
import os
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from src.tools.dep import *


def check_pkgs():
    os.system('pip install -r requirements.txt --upgrade')


def check_folder(path: str, can_retry: bool = True):
    if os.path.isdir(path):
        return True
    if os.path.exists(path):
        logger.logger.warning(f"{path}被文件占用，将其强行移除。")
        os.remove(path)
        if not can_retry:
            return False
        return check_folder(path, can_retry=False)
    os.mkdir(path)
    return True


def check_folders(folder_nest: dict, parent_path: str = None):

    if not parent_path:
        parent_path = ""
    else:
        parent_path = f"{parent_path}{os.sep}"
    logger.info(f"初始化系统文件夹:{parent_path}")
    for f in folder_nest:
        new_parent = f"{parent_path}{f}"
        check_folder(new_parent)
        children = folder_nest[f]
        if isinstance(children, dict):
            check_folders(children, new_parent)


init_folders = {
    "./src": {
        "data": None,
        "cache": None,
        "sign": None,
        "assets": {
            "jx3": {
                "bg": None,
                "kungfu": None,
                "skills": None,
                "icons": None,
                "achievement": None,
                "talents": None,
                "adventure": None,
                "serendipity": None,
                "pvx": {
                    "flower": None
                }
            },
            "wuxingshi": None
        },
        "plugins": None
    }
}

check_pkgs()
check_folders(init_folders)
logger.debug('check plugins document')
plugins = os.listdir("./src/plugins")
for i in plugins:
    if not os.path.exists(f"./src/plugins/{i}/info.json"):
        raise FileNotFoundError(
            f"Plugin `{i}` required a `info.json` but not found. Please check and try again.")
        sys.exit(1)

logger.debug('start nonebot...')
app = nonebot.get_asgi()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
nonebot.load_from_toml("pyproject.toml")
if __name__ == "__main__":
    nonebot.logger.warning(
        "Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")
