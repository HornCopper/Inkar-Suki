from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.log import logger

import nonebot
import os

if not os.path.exists("./src/config/config.yml"):
    with open("./src/assets/source/config.yml", mode = "r", encoding = "utf-8") as f:
        template = f.read()
    with open("./src/config/config.yml", mode = "w", encoding = "utf-8") as f:
        f.write(template)
    logger.error("未检测到`Inkar Suki`配置文件！已在`src/config`目录下生成`config.yml`，请填写完毕后重新启动！")
    os._exit(0)

from src.config import Config

qq_options = Config.qq_official.nonebot_options()
qq_bots = qq_options.pop("qq_bots", None)
nonebot.init(**qq_options)
logger.debug("start nonebot...")
app = nonebot.get_asgi()
driver = nonebot.get_driver()
if qq_bots is not None:
    # 初始化调试日志会打印配置；凭证在初始化完成后注入，避免输出 AppSecret。
    driver.config.qq_bots = qq_bots
driver.register_adapter(ONEBOT_V11Adapter)

from src.utils.dispatch import install_command_prefilter

install_command_prefilter()

if Config.qq_official.enabled:
    from src.adapters.qq_official.adapter import Adapter as QQAdapter
    from src.adapters.qq_official import install_bridge

    driver.register_adapter(QQAdapter)
    install_bridge()

nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.run(app = "__mp_main__:app")
