from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.log import logger

import nonebot
import os

if not os.path.exists("./src/config/config.yml"):
    with open("./src/assets/source/config.yml", mode="r", encoding="utf-8") as f:
        template = f.read()
    with open("./src/config/config.yml", mode="w", encoding="utf-8") as f:
        f.write(template)
    logger.error("未检测到`Inkar Suki`配置文件！已在`src/config`目录下生成`config.yml`，请填写完毕后重新启动！")
    os._exit(0)

nonebot.init()
logger.debug("start nonebot...")
app = nonebot.get_asgi()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")