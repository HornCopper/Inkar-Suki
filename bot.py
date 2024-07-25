import os
import nonebot
import sys

from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.log import logger


config_path = f"{os.getcwd()}/src/tools/config/config.yml"

if not os.path.exists(config_path):
    nonebot.logger.error("未配置Inkar Suki配置文件，请修改`src/tools/config/_config.yml`后再次运行，特别注意该配置文件的第一行注释！")
    os._exit(0)

def ensure_folder_exists(path: str, can_retry: bool = True) -> bool:
    """
    检查并创建文件夹
    """
    if os.path.isdir(path):
        return True
    if os.path.exists(path):
        os.remove(path)
        if not can_retry:
            return False
        return ensure_folder_exists(path, can_retry=False)
    os.mkdir(path)
    return True

def ensure_folders_exist(folder_structure: dict, parent_path: str = ""):
    """
    递归检查并创建文件夹结构
    """
    for folder, children in folder_structure.items():
        current_path = os.path.join(parent_path, folder)
        ensure_folder_exists(current_path)
        if isinstance(children, dict):
            ensure_folders_exist(children, current_path)

folder_structure = {
    "src": {
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

ensure_folders_exist(folder_structure)

nonebot.init()
logger.debug("start nonebot...")
app = nonebot.get_asgi()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")
