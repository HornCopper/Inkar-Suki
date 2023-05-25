#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import nonebot
import sys
from src.tools.config import Config
import os
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from sgtpyutils import logger

tools_path: str = None


def init_env():
    logger.logger.info('检查和初始化环境')
    global tools_path
    tools_path = os.path.dirname(__file__)
    # sys.path.append(os.path.join(tools_path, f'src'))
    tools_path = os.path.join(tools_path, f'src{os.sep}tools')
    sys.path.append(tools_path)
    # src.db.init_database(Config.database)
init_env()
def check_folder(path: str, can_retry: bool = True):
    if os.path.isdir(path):
        return True
    if os.path.exists(path):
        logger.logger.warn(f'{path}被文件占用，将其强行移除。')
        os.remove(path)
        if not can_retry:
            return False
        return check_folder(path, can_retry=False)
    os.mkdir(path)
    return True


def check_folders(folder_nest: dict, parent_path: str = None):
    
    if not parent_path:
        parent_path = ''
    else:
        parent_path = f'{parent_path}{os.sep}'
    logger.logger.info(f'初始化系统文件夹:{parent_path}')
    for f in folder_nest:
        new_parent = f'{parent_path}{f}'
        check_folder(new_parent)
        children = folder_nest[f]
        if isinstance(children, dict):
            check_folders(children, new_parent)
init_folders = {
        './src': {
            'data': None,
            'cache': None,
            'sign': None,
            'assets': {
                'jx3': {
                    'skills': None,
                    'icons': None,
                    'achievement': None,
                    'talents': None,
                    'adventure': None,
                }
            },
            'plugins': None
        }
    }
check_folders(init_folders)

plugins = os.listdir('./src/plugins')
for i in plugins:
    if not os.path.exists(f'./src/plugins/{i}/info.json'):
        raise FileNotFoundError(
            f"Plugin `{i}` required a `info.json` but not found. Please check and try again.")
        sys.exit(1)


nonebot.init(tools_path=tools_path, log_level='DEBUG')
app = nonebot.get_asgi()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
nonebot.load_from_toml("pyproject.toml")
if __name__ == "__main__":
    nonebot.logger.warning(
        "Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")
